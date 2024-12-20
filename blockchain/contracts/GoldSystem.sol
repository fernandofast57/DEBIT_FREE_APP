
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

contract NobleGoldSystem is Ownable, ReentrancyGuard {
    using SafeMath for uint256;

    struct Investment {
        uint256 euroAmount;
        uint256 goldGrams;
        uint256 timestamp;
        bool isVerified;
    }

    struct Noble {
        string rank;
        uint256 totalVolume;
        uint256 directReferrals;
        address upline;
        bool kycVerified;
        string ibanHash;
    }

    mapping(address => Investment[]) public investments;
    mapping(address => Noble) public nobles;
    mapping(address => address[]) public referrals;
    mapping(address => bool) public verifiedAccounts;
    
    uint256 public constant CLIENT_SHARE = 933; // 93.3%
    uint256 public constant NETWORK_SHARE = 67; // 6.7%
    uint256 public constant BASIS_POINTS = 1000;
    
    event KYCVerified(address indexed user);
    event IBANVerified(address indexed user);
    event GoldTransformed(
        address indexed user,
        uint256 euroAmount,
        uint256 goldGrams,
        uint256 timestamp
    );
    event BonusDistributed(
        address indexed user,
        address indexed referrer,
        uint256 amount,
        string bonusType
    );

    constructor() Ownable(msg.sender) {}

    modifier onlyVerifiedUser(address user) {
        require(verifiedAccounts[user], "User not verified");
        require(nobles[user].kycVerified, "KYC not completed");
        _;
    }

    function verifyKYC(address user) external onlyOwner {
        nobles[user].kycVerified = true;
        emit KYCVerified(user);
    }

    function verifyIBAN(address user, string memory ibanHash) external onlyOwner {
        nobles[user].ibanHash = ibanHash;
        emit IBANVerified(user);
    }

    function transformGold(
        address user,
        uint256 euroAmount,
        uint256 goldGrams
    ) external onlyOwner onlyVerifiedUser(user) nonReentrant {
        require(euroAmount > 0, "Invalid euro amount");
        require(goldGrams > 0, "Invalid gold amount");

        uint256 clientGold = goldGrams.mul(CLIENT_SHARE).div(BASIS_POINTS);
        uint256 networkGold = goldGrams.mul(NETWORK_SHARE).div(BASIS_POINTS);

        investments[user].push(Investment({
            euroAmount: euroAmount,
            goldGrams: clientGold,
            timestamp: block.timestamp,
            isVerified: true
        }));

        _distributeNetworkBonus(user, networkGold);
        
        emit GoldTransformed(user, euroAmount, clientGold, block.timestamp);
    }

    function _distributeNetworkBonus(address user, uint256 networkGold) internal {
        address current = nobles[user].upline;
        uint256 level = 0;
        uint256[] memory bonusRates = new uint256[](3);
        bonusRates[0] = 7; // 0.7%
        bonusRates[1] = 5; // 0.5%
        bonusRates[2] = 5; // 0.5%

        while (current != address(0) && level < 3) {
            uint256 bonus = networkGold.mul(bonusRates[level]).div(1000);
            nobles[current].totalVolume = nobles[current].totalVolume.add(bonus);
            
            emit BonusDistributed(user, current, bonus, nobles[current].rank);
            
            current = nobles[current].upline;
            level++;
        }
    }
}
