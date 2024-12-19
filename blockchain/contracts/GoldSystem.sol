
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
    }

    struct Noble {
        string rank;
        uint256 totalVolume;
        uint256 directReferrals;
        address upline;
    }

    mapping(address => Investment[]) public investments;
    mapping(address => Noble) public nobles;
    mapping(address => address[]) public referrals;

    event GoldTransformed(
        address indexed user,
        uint256 euroAmount,
        uint256 goldGrams,
        uint256 timestamp
    );

    event RankUpdated(
        address indexed user,
        string oldRank,
        string newRank
    );

    event BonusDistributed(
        address indexed user,
        address indexed referrer,
        uint256 amount,
        string bonusType
    );

    uint256 public constant ORGANIZATION_FEE = 50;
    uint256 public constant AFFILIATE_FEE = 17;
    uint256 public constant FEE_DENOMINATOR = 1000;

    constructor() Ownable(msg.sender) {}

    function batchTransform(
        address[] calldata users,
        uint256[] calldata euroAmounts,
        uint256[] calldata goldGrams
    ) external onlyOwner nonReentrant {
        require(users.length == euroAmounts.length && euroAmounts.length == goldGrams.length, 
                "Arrays length mismatch");

        for (uint i = 0; i < users.length; i++) {
            _transform(users[i], euroAmounts[i], goldGrams[i]);
        }
    }

    function _transform(
        address user,
        uint256 euroAmount,
        uint256 goldGrams
    ) internal {
        require(euroAmount > 0, "Amount must be greater than 0");
        require(goldGrams > 0, "Gold grams must be greater than 0");

        investments[user].push(Investment({
            euroAmount: euroAmount,
            goldGrams: goldGrams,
            timestamp: block.timestamp
        }));

        _distributeBonus(user, euroAmount);
        _updateRank(user);

        emit GoldTransformed(user, euroAmount, goldGrams, block.timestamp);
    }

    function _updateRank(address user) internal {
        Noble storage noble = nobles[user];
        string memory newRank = noble.rank;

        if (noble.totalVolume >= 100000 ether && noble.directReferrals >= 10) {
            newRank = "count";
        } else if (noble.totalVolume >= 50000 ether && noble.directReferrals >= 5) {
            newRank = "viscount";
        } else if (noble.totalVolume >= 10000 ether && noble.directReferrals >= 2) {
            newRank = "noble";
        }

        if (keccak256(bytes(noble.rank)) != keccak256(bytes(newRank))) {
            string memory oldRank = noble.rank;
            noble.rank = newRank;
            emit RankUpdated(user, oldRank, newRank);
        }
    }

    function _distributeBonus(address user, uint256 amount) internal {
        address current = nobles[user].upline;
        uint256 level = 0;

        while (current != address(0) && level < 7) {
            uint256 bonus = amount.mul(AFFILIATE_FEE).div(FEE_DENOMINATOR);
            
            if (keccak256(bytes(nobles[current].rank)) == keccak256(bytes("count"))) {
                bonus = bonus.mul(2);
            } else if (keccak256(bytes(nobles[current].rank)) == keccak256(bytes("viscount"))) {
                bonus = bonus.mul(15).div(10);
            }

            nobles[current].totalVolume = nobles[current].totalVolume.add(amount);
            
            emit BonusDistributed(user, current, bonus, nobles[current].rank);
            
            current = nobles[current].upline;
            level++;
        }
    }

    function registerReferral(address user, address referrer) external onlyOwner {
        require(user != address(0) && referrer != address(0), "Invalid addresses");
        require(nobles[user].upline == address(0), "Referral already registered");
        require(user != referrer, "Cannot refer yourself");

        nobles[user].upline = referrer;
        referrals[referrer].push(user);
        nobles[referrer].directReferrals = nobles[referrer].directReferrals.add(1);

        _updateRank(referrer);
    }

    function getInvestments(address user) external view returns (Investment[] memory) {
        return investments[user];
    }

    function getNobleInfo(address user) external view returns (
        string memory rank,
        uint256 totalVolume,
        uint256 directReferrals,
        address upline
    ) {
        Noble storage noble = nobles[user];
        return (noble.rank, noble.totalVolume, noble.directReferrals, noble.upline);
    }

    function getReferrals(address user) external view returns (address[] memory) {
        return referrals[user];
    }
}
