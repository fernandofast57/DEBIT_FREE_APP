
// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

contract GoldSystem {
    address public owner;
    mapping(address => uint256) public euroBalances;
    mapping(address => uint256) public goldBalances;
    uint256 public lastFixingPrice;
    
    event BatchTransform(
        address[] users,
        uint256[] euroAmounts,
        uint256[] goldAmounts,
        uint256 fixingPrice
    );
    
    constructor() {
        owner = msg.sender;
    }
    
    modifier onlyOwner() {
        require(msg.sender == owner, "Only owner");
        _;
    }
    
    function batchTransform(
        address[] calldata users,
        uint256[] calldata euroAmounts,
        uint256[] calldata goldAmounts,
        uint256 fixingPrice
    ) external onlyOwner {
        require(
            users.length == euroAmounts.length && 
            users.length == goldAmounts.length,
            "Arrays length mismatch"
        );
        
        lastFixingPrice = fixingPrice;
        
        for(uint i = 0; i < users.length; i++) {
            euroBalances[users[i]] += euroAmounts[i];
            goldBalances[users[i]] += goldAmounts[i];
        }
        
        emit BatchTransform(users, euroAmounts, goldAmounts, fixingPrice);
    }
}
