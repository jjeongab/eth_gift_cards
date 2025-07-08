pragma solidity ^0.8.0;

contract GiftCard {
    mapping(bytes32 => uint256) private giftCards;
    mapping(bytes32 => bool) private redeemed;
    
    event GiftCardPurchased(bytes32 indexed codeHash, uint256 value);
    event GiftCardRedeemed(bytes32 indexed codeHash, address redeemer, uint256 value);
    
    function buy(bytes32 codeHash) public payable {
        require(msg.value >= 0.001 ether, "Minimum gift card value is 0.001 ETH");
        require(giftCards[codeHash] == 0, "Gift card already exists");
        
        giftCards[codeHash] = msg.value;
        emit GiftCardPurchased(codeHash, msg.value);
    }
    
    function redeem(string memory code) public {
        bytes32 codeHash = keccak256(abi.encodePacked(code));
        
        require(giftCards[codeHash] > 0, "Gift card does not exist");
        require(!redeemed[codeHash], "Gift card already redeemed");
        
        uint256 value = giftCards[codeHash];
        redeemed[codeHash] = true;
        
        (bool success, ) = msg.sender.call{value: value}("");
        require(success, "Transfer failed");
        
        emit GiftCardRedeemed(codeHash, msg.sender, value);
    }
    
    function getGiftCardValue(bytes32 codeHash) public view returns (uint256) {
        return giftCards[codeHash];
    }
    
    function isRedeemed(bytes32 codeHash) public view returns (bool) {
        return redeemed[codeHash];
    }
}