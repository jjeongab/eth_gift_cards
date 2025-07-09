# Ethereum Gift Card System

A decentralized gift card system built on Ethereum that allows users to purchase and redeem gift cards using unique codes.

## Features

- Buy gift cards with ETH using unique codes
- Redeem gift cards to receive ETH
- Minimum gift card value: 0.001 ETH
- Each code can only be used once
- Web interface with MetaMask integration
- Comprehensive test suite

## How to Use This System

1. **For Deployment:**
   - Run `npm install` to install dependencies
   - Run `npm run node` to start local Hardhat network
   - Run `npm run deploy` to deploy the contract
   - Run `npm run serve` to start the web server
   - Update the contract address in `index.html`

2. **For Testing:**
   - Run the Python tests with `python tests/giftcard_test.py`
   - The Selenium tests require the web server running

3. **For Demo:**
   - Connect MetaMask to localhost:8545
   - Import a Hardhat test account (private keys shown in Hardhat console)
   - Buy a gift card with a code like "GIFT123" and 0.01 ETH
   - Switch to another account and redeem with the same code

The system is intentionally simple but fully functional. It demonstrates understanding of Solidity, Web3 integration, and testing practices while being easy to explain in an interview setting.