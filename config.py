# config.py

# Network
INFURA_URL = "https://mainnet.infura.io/v3/46cf637ae822413aaf2a2be4d1451db1"

# Telegram Config
TELEGRAM_TOKEN = "7989561364:AAEZmzGPE7JhTQ0k4hec54-mTP55gCMdU-U"
TELEGRAM_CHAT_ID = "303453465"

# Exchange Routers
ROUTERS = {
    "Uniswap": "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D",
    "SushiSwap": "0xd9e1cE17f2641f24aE83637ab66a2cca9C378B9F",
    "PancakeSwap": "0xEfF92A263d31888d860bD50809A8D171709b7b1c"
}

# Trading settings
MIN_PROFIT_USD = 0.000001
CHECK_INTERVAL = 5  # seconds between checks
DEFAULT_AMOUNT = 0.1  # ETH amount to check for arbitrage

# Router ABI for price checking
ROUTER_ABI = '''[
    {
        "inputs": [
            {"internalType": "uint256", "name": "amountIn", "type": "uint256"},
            {"internalType": "address[]", "name": "path", "type": "address[]"}
        ],
        "name": "getAmountsOut",
        "outputs": [
            {"internalType": "uint256[]", "name": "amounts", "type": "uint256[]"}
        ],
        "stateMutability": "view",
        "type": "function"
    }
]'''