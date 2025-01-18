
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/token/ERC20/IERC20.sol";
import "@openzeppelin/contracts/access/AccessControl.sol";
import "@openzeppelin/contracts/security/Pausable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";

contract GoldSystem is AccessControl, Pausable, ReentrancyGuard {
    bytes32 public constant OPERATOR_ROLE = keccak256("OPERATOR_ROLE");
    
    struct Noble {
        string rank;
        address upline;
        uint256 totalInvestment;
        uint256 lastUpdateTime;
    }
    
    struct GoldTransaction {
        uint256 euroAmount;
        uint256 goldGrams;
        uint256 timestamp;
        string transactionType;
    }
    
    mapping(address => Noble) public nobles;
    mapping(address => GoldTransaction[]) private transactions;
    mapping(address => uint256) public goldBalances;
    
    uint256 public constant MINIMUM_INVESTMENT = 1000 ether;
    uint256 public constant MAX_TRANSACTION_AMOUNT = 1000000 ether;
    
    event NobleRankUpdated(address indexed user, string newRank, uint256 timestamp);
    event GoldTransactionExecuted(
        address indexed user,
        uint256 euroAmount,
        uint256 goldGrams,
        string transactionType,
        uint256 timestamp
    );
    
    constructor() {
        _grantRole(DEFAULT_ADMIN_ROLE, msg.sender);
        _grantRole(OPERATOR_ROLE, msg.sender);
    }
    
    modifier validAmount(uint256 amount) {
        require(amount > 0, "Amount must be positive");
        require(amount <= MAX_TRANSACTION_AMOUNT, "Amount exceeds maximum limit");
        _;
    }
    
    modifier validAddress(address addr) {
        require(addr != address(0), "Invalid address");
        require(addr != address(this), "Cannot be contract address");
        _;
    }
    
    function executeGoldTransaction(
        address user,
        uint256 euroAmount,
        uint256 goldGrams,
        string memory transactionType
    ) external onlyRole(OPERATOR_ROLE) whenNotPaused nonReentrant validAddress(user) validAmount(euroAmount) {
        require(bytes(transactionType).length > 0, "Transaction type required");
        
        goldBalances[user] += goldGrams;
        
        transactions[user].push(GoldTransaction({
            euroAmount: euroAmount,
            goldGrams: goldGrams,
            timestamp: block.timestamp,
            transactionType: transactionType
        }));
        
        emit GoldTransactionExecuted(
            user,
            euroAmount,
            goldGrams,
            transactionType,
            block.timestamp
        );
    }
    
    function updateNobleRank(
        address user,
        string calldata newRank,
        address upline
    ) external onlyRole(OPERATOR_ROLE) whenNotPaused validAddress(user) {
        require(bytes(newRank).length > 0, "Rank cannot be empty");
        if(upline != address(0)) {
            require(nobles[upline].lastUpdateTime > 0, "Invalid upline");
        }
        
        nobles[user].rank = newRank;
        nobles[user].upline = upline;
        nobles[user].lastUpdateTime = block.timestamp;
        
        emit NobleRankUpdated(user, newRank, block.timestamp);
    }
    
    function getTransactionHistory(address user) 
        external 
        view 
        validAddress(user) 
        returns (GoldTransaction[] memory) 
    {
        return transactions[user];
    }
    
    function getNobleUpline(address user) 
        external 
        view 
        validAddress(user) 
        returns (address) 
    {
        return nobles[user].upline;
    }
    
    function pause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _pause();
    }
    
    function unpause() external onlyRole(DEFAULT_ADMIN_ROLE) {
        _unpause();
    }
}
