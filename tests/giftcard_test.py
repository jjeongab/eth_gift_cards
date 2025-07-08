import pytest
from web3 import Web3
from eth_utils import keccak
import json

# Hardhat local network configuration
HARDHAT_URL = "http://127.0.0.1:8545"
CONTRACT_ADDRESS = "0x5FbDB2315678afecb367f032d93F642f64180aa3"  # Default first deployment address

# Contract ABI
CONTRACT_ABI = [
    {
        "inputs": [{"internalType": "bytes32", "name": "codeHash", "type": "bytes32"}],
        "name": "buy",
        "outputs": [],
        "stateMutability": "payable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "string", "name": "code", "type": "string"}],
        "name": "redeem",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "codeHash", "type": "bytes32"}],
        "name": "getGiftCardValue",
        "outputs": [{"internalType": "uint256", "name": "", "type": "uint256"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [{"internalType": "bytes32", "name": "codeHash", "type": "bytes32"}],
        "name": "isRedeemed",
        "outputs": [{"internalType": "bool", "name": "", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    }
]

class TestGiftCard:
    def setup_method(self):
        """Set up test fixtures"""
        self.w3 = Web3(Web3.HTTPProvider(HARDHAT_URL))
        assert self.w3.is_connected(), "Failed to connect to Hardhat network"
        
        # Get test accounts from Hardhat
        self.buyer = self.w3.eth.accounts[0]
        self.redeemer = self.w3.eth.accounts[1]
        
        # Initialize contract
        self.contract = self.w3.eth.contract(
            address=CONTRACT_ADDRESS,
            abi=CONTRACT_ABI
        )
    
    def get_code_hash(self, code):
        """Helper function to get keccak256 hash of code"""
        return self.w3.keccak(text=code)
    
    def test_buy_gift_card(self):
        """Test buying a gift card"""
        code = "GIFT123"
        code_hash = self.get_code_hash(code)
        value = self.w3.to_wei(0.1, 'ether')
        
        # Buy gift card
        tx_hash = self.contract.functions.buy(code_hash).transact({
            'from': self.buyer,
            'value': value
        })
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Check gift card value
        stored_value = self.contract.functions.getGiftCardValue(code_hash).call()
        assert stored_value == value
        
        # Check not redeemed
        is_redeemed = self.contract.functions.isRedeemed(code_hash).call()
        assert not is_redeemed
    
    def test_redeem_gift_card(self):
        """Test redeeming a gift card"""
        code = "REDEEM123"
        code_hash = self.get_code_hash(code)
        value = self.w3.to_wei(0.05, 'ether')
        
        # Buy gift card first
        tx_hash = self.contract.functions.buy(code_hash).transact({
            'from': self.buyer,
            'value': value
        })
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Get redeemer's initial balance
        initial_balance = self.w3.eth.get_balance(self.redeemer)
        
        # Redeem gift card
        tx_hash = self.contract.functions.redeem(code).transact({
            'from': self.redeemer
        })
        receipt = self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Calculate gas cost
        gas_cost = receipt['gasUsed'] * self.w3.eth.gas_price
        
        # Check redeemer received funds (minus gas)
        final_balance = self.w3.eth.get_balance(self.redeemer)
        expected_balance = initial_balance + value - gas_cost
        assert abs(final_balance - expected_balance) < self.w3.to_wei(0.001, 'ether')
        
        # Check gift card is marked as redeemed
        is_redeemed = self.contract.functions.isRedeemed(code_hash).call()
        assert is_redeemed
    
    def test_minimum_value_requirement(self):
        """Test that gift cards must have minimum value"""
        code = "TOOSMALL"
        code_hash = self.get_code_hash(code)
        value = self.w3.to_wei(0.0009, 'ether')  # Below minimum
        
        # Should fail
        with pytest.raises(Exception) as excinfo:
            self.contract.functions.buy(code_hash).transact({
                'from': self.buyer,
                'value': value
            })
        assert "Minimum gift card value is 0.001 ETH" in str(excinfo.value)
    
    def test_cannot_buy_duplicate(self):
        """Test that same code cannot be used twice"""
        code = "DUPLICATE"
        code_hash = self.get_code_hash(code)
        value = self.w3.to_wei(0.01, 'ether')
        
        # Buy first gift card
        tx_hash = self.contract.functions.buy(code_hash).transact({
            'from': self.buyer,
            'value': value
        })
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Try to buy again with same code
        with pytest.raises(Exception) as excinfo:
            self.contract.functions.buy(code_hash).transact({
                'from': self.buyer,
                'value': value
            })
        assert "Gift card already exists" in str(excinfo.value)
    
    def test_cannot_redeem_twice(self):
        """Test that gift card cannot be redeemed twice"""
        code = "ONETIME"
        code_hash = self.get_code_hash(code)
        value = self.w3.to_wei(0.02, 'ether')
        
        # Buy and redeem once
        tx_hash = self.contract.functions.buy(code_hash).transact({
            'from': self.buyer,
            'value': value
        })
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        tx_hash = self.contract.functions.redeem(code).transact({
            'from': self.redeemer
        })
        self.w3.eth.wait_for_transaction_receipt(tx_hash)
        
        # Try to redeem again
        with pytest.raises(Exception) as excinfo:
            self.contract.functions.redeem(code).transact({
                'from': self.buyer
            })
        assert "Gift card already redeemed" in str(excinfo.value)
    
    def test_cannot_redeem_nonexistent(self):
        """Test that non-existent gift cards cannot be redeemed"""
        code = "DOESNOTEXIST"
        
        with pytest.raises(Exception) as excinfo:
            self.contract.functions.redeem(code).transact({
                'from': self.redeemer
            })
        assert "Gift card does not exist" in str(excinfo.value)

if __name__ == "__main__":
    pytest.main([__file__, "-v"])