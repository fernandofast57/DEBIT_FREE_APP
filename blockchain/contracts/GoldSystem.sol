
pragma solidity ^0.8.0;

contract GoldSystem {
    mapping(address => uint256) public goldBalances;
    
    event BatchTransform(
        address[] users,
        uint96[] euroAmounts, 
        uint96[] goldAmounts,
        uint32 fixingPrice,
        uint32 timestamp
    );

    function batchTransform(
        address[] calldata users,
        uint96[] calldata euroAmounts,
        uint96[] calldata goldAmounts,
        uint32 fixingPrice
    ) external {
        require(users.length == euroAmounts.length && users.length == goldAmounts.length, "Invalid arrays");
        require(users.length <= 50, "Batch too large");
        
        uint32 timestamp = uint32(block.timestamp);
        
        for(uint i = 0; i < users.length; i++) {
            goldBalances[users[i]] += goldAmounts[i];
        }
        
        emit BatchTransform(users, euroAmounts, goldAmounts, fixingPrice, timestamp);
    }
}
