# Crypto DEX Arbitrage Monitor

A Telegram-based monitoring system that tracks price differences across major decentralized exchanges (Uniswap, SushiSwap, and PancakeSwap) to identify arbitrage opportunities in real-time.

## Key Features
- Live price monitoring of crypto pairs across multiple DEXs
- Instant notifications of arbitrage opportunities via Telegram
- Support for custom token pairs
- Price difference calculations with ROI percentage
- Individual monitoring lists for different users
- Real-time price updates every 5 seconds

## How It Works

### 1. Price Monitoring
The system continuously checks prices for selected token pairs across three major DEXs:
- Uniswap V2
- SushiSwap 
- PancakeSwap

### 2. Arbitrage Detection 
When price differences between exchanges exceed the minimum threshold, the system identifies potential arbitrage opportunities considering:
- Price spreads between exchanges
- Potential ROI
- Trading volume availability

### 3. Notification System
Users receive real-time updates through Telegram, including:
- Current prices across all monitored exchanges
- Profitable arbitrage opportunities
- ROI calculations for each opportunity

### 4. User Control
Through Telegram commands, users can:
- Add/remove token pairs to monitor
- View current price information
- Get instant notifications of profitable opportunities

## Technical Implementation
- Built with Python using Web3.py for blockchain interaction
- Integrates with Ethereum network through Infura
- Uses Telegram Bot API for user interface
- Implements smart contract interactions with DEX routers

## Use Case
Perfect for traders and investors who want to:
- Monitor DEX price differences
- Identify trading opportunities across exchanges
- Get real-time alerts for profitable trades
- Track specific token pairs of interest

This tool serves as both a monitoring system and a decision-support tool for crypto arbitrage trading, helping users identify and act on price inefficiencies in the DeFi market.