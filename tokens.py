# tokens.py
from dataclasses import dataclass

@dataclass
class Token:
    address: str
    symbol: str
    decimals: int

@dataclass
class TradingPair:
    base: Token
    quote: Token
    min_amount: float
    max_amount: float

    def __str__(self):
        return f"{self.base.symbol}-{self.quote.symbol}"

# Most liquid and widely available tokens
TOKENS = {
    "WETH": Token(
        address="0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2",
        symbol="WETH",
        decimals=18
    ),
    "USDT": Token(
        address="0xdAC17F958D2ee523a2206206994597C13D831ec7",
        symbol="USDT",
        decimals=6
    ),
    "USDC": Token(
        address="0xA0b86991c6218b36c1d19D4a2e9Eb0cE3606eB48",
        symbol="USDC",
        decimals=6
    ),
    "DAI": Token(
        address="0x6B175474E89094C44Da98b954EedeAC495271d0F",
        symbol="DAI",
        decimals=18
    ),
    "BUSD": Token(
        address="0x4Fabb145d64652a948d72533023f6E7A623C7C53",
        symbol="BUSD",
        decimals=18
    )
}

# Focus on the most liquid stablecoin pairs that are available across exchanges
TRADING_PAIRS = [
    # WETH - Stablecoin pairs (highly liquid across all exchanges)
    TradingPair(
        base=TOKENS["WETH"],
        quote=TOKENS["USDT"],
        min_amount=0.1,
        max_amount=10
    ),
    TradingPair(
        base=TOKENS["WETH"],
        quote=TOKENS["USDC"],
        min_amount=0.1,
        max_amount=10
    ),
    # Stablecoin pairs (usually available and good for arbitrage)
    TradingPair(
        base=TOKENS["USDC"],
        quote=TOKENS["USDT"],
        min_amount=1000,
        max_amount=100000
    ),
    TradingPair(
        base=TOKENS["BUSD"],
        quote=TOKENS["USDT"],
        min_amount=1000,
        max_amount=100000
    ),
    TradingPair(
        base=TOKENS["DAI"],
        quote=TOKENS["USDC"],
        min_amount=1000,
        max_amount=100000
    )
]

# Price validation ranges
PRICE_RANGES = {
    "WETH-USDT": {"min": 1000, "max": 5000},
    "WETH-USDC": {"min": 1000, "max": 5000},
    "USDC-USDT": {"min": 0.95, "max": 1.05},
    "BUSD-USDT": {"min": 0.95, "max": 1.05},
    "DAI-USDC": {"min": 0.95, "max": 1.05}
}