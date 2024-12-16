// SPDX-License-Identifier: MIT
pragma solidity ^0.8.0;

contract GoldSystem {
    struct Transaction {
        uint32 timestamp;
        uint96 euroAmount;
        uint96 goldGrams;
        uint32 fixingPrice;
    }

    mapping(address => Transaction[]) public userTransactions;
    address public admin;

    event TransformationExecuted(
        address indexed user,
        uint96 euroAmount,
        uint96 goldGrams,
        uint32 fixingPrice,
        uint32 timestamp
    );

    constructor() {
        admin = msg.sender;
    }

    modifier onlyAdmin() {
        require(msg.sender == admin, "Solo admin");
        _;
    }

    // Batch processing per ottimizzare i costi del gas
    function batchTransform(
        address[] calldata users,
        uint96[] calldata euroAmounts,
        uint96[] calldata goldGrams,
        uint32 fixingPrice
    ) external onlyAdmin {
        require(
            users.length == euroAmounts.length && 
            users.length == goldGrams.length,
            "Array lunghezze non corrispondenti"
        );

        uint32 timestamp = uint32(block.timestamp);

        for(uint i = 0; i < users.length; i++) {
            Transaction memory newTx = Transaction({
                timestamp: timestamp,
                euroAmount: euroAmounts[i],
                goldGrams: goldGrams[i],
                fixingPrice: fixingPrice
            });

            userTransactions[users[i]].push(newTx);

            emit TransformationExecuted(
                users[i],
                euroAmounts[i],
                goldGrams[i],
                fixingPrice,
                timestamp
            );
        }
    }

    function getUserTransactions(address user) 
        external 
        view 
        returns (Transaction[] memory) 
    {
        return userTransactions[user];
    }
}