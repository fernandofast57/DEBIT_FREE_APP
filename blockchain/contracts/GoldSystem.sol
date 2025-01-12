
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;

import "@openzeppelin/contracts/access/Ownable.sol";
import "@openzeppelin/contracts/security/ReentrancyGuard.sol";
import "@openzeppelin/contracts/utils/math/SafeMath.sol";

contract NobleGoldSystem is Ownable, ReentrancyGuard {
    using SafeMath for uint256;

    struct GoldTransaction {
        uint256 euroAmount;
        uint256 goldGrams;
        uint256 fixingPrice;
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

    mapping(address => GoldTransaction[]) public transactions;
    mapping(address => Noble) public nobles;
    mapping(address => address[]) public referrals;
    
    uint256 public constant CLIENT_SHARE = 933; // 93.3%
    uint256 public constant NETWORK_SHARE = 17; // 1.7%
    uint256 public constant OPERATIONAL_SHARE = 50; // 5%
    uint256 public constant BASIS_POINTS = 1000;
    
    event GoldTransformed(
        address indexed user,
        uint256 euroAmount,
        uint256 goldGrams,
        uint256 fixingPrice,
        uint256 timestamp
    );
    
    event BonusDistributed(
        address indexed user,
        address indexed referrer,
        uint256 amount,
        string bonusType
    );
    
    event NobleRankUpdated(
        address indexed user,
        string newRank,
        uint256 timestamp
    );

    constructor() Ownable(msg.sender) {}

    function transformGold(
        address user,
        uint256 euroAmount,
        uint256 goldGrams,
        uint256 fixingPrice
    ) external onlyOwner nonReentrant {
        require(euroAmount > 0, "Invalid euro amount");
        require(goldGrams > 0, "Invalid gold amount");

        uint256 clientGold = goldGrams.mul(CLIENT_SHARE).div(BASIS_POINTS);
        uint256 networkGold = goldGrams.mul(NETWORK_SHARE).div(BASIS_POINTS);
        
        transactions[user].push(GoldTransaction({
            euroAmount: euroAmount,
            goldGrams: clientGold,
            fixingPrice: fixingPrice,
            timestamp: block.timestamp,
            isVerified: true
        }));

        _distributeNetworkBonus(user, networkGold);
        
        emit GoldTransformed(user, euroAmount, clientGold, fixingPrice, block.timestamp);
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

    function getTransactionHistory(address user) external view returns (
        uint256[] memory euroAmounts,
        uint256[] memory goldGrams,
        uint256[] memory timestamps
    ) {
        GoldTransaction[] storage userTxs = transactions[user];
        uint256 length = userTxs.length;
        
        euroAmounts = new uint256[](length);
        goldGrams = new uint256[](length);
        timestamps = new uint256[](length);
        
        for (uint256 i = 0; i < length; i++) {
            euroAmounts[i] = userTxs[i].euroAmount;
            goldGrams[i] = userTxs[i].goldGrams;
            timestamps[i] = userTxs[i].timestamp;
        }
        
        return (euroAmounts, goldGrams, timestamps);
    }

    function updateNobleRank(address user, string calldata newRank) external onlyOwner {
        nobles[user].rank = newRank;
        emit NobleRankUpdated(user, newRank, block.timestamp);
    }
}
