# tokens.py
from dataclasses import dataclass
from typing import Dict, Optional
import json
import os


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


class TokenManager:
    def __init__(self):
        # Default tokens that are always available
        self.default_tokens = {
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
        }

        # Load custom tokens
        self.custom_tokens = self.load_custom_tokens()

    @property
    def all_tokens(self) -> Dict[str, Token]:
        """Get all available tokens (default + custom)"""
        return {**self.default_tokens, **self.custom_tokens}

    def load_custom_tokens(self) -> Dict[str, Token]:
        """Load custom tokens from file"""
        try:
            if os.path.exists('custom_tokens.json'):
                with open('custom_tokens.json', 'r') as f:
                    data = json.load(f)
                    return {
                        symbol: Token(**token_data)
                        for symbol, token_data in data.items()
                    }
        except Exception as e:
            print(f"Error loading custom tokens: {e}")
        return {}

    def save_custom_tokens(self):
        """Save custom tokens to file"""
        try:
            data = {
                symbol: {
                    "address": token.address,
                    "symbol": token.symbol,
                    "decimals": token.decimals
                }
                for symbol, token in self.custom_tokens.items()
            }
            with open('custom_tokens.json', 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving custom tokens: {e}")

    def add_token(self, symbol: str, address: str, decimals: int) -> Token:
        """Add new custom token"""
        if symbol in self.default_tokens:
            raise ValueError(f"Token {symbol} already exists in default tokens")

        if symbol in self.custom_tokens:
            raise ValueError(f"Token {symbol} already exists in custom tokens")

        token = Token(address=address, symbol=symbol, decimals=decimals)
        self.custom_tokens[symbol] = token
        self.save_custom_tokens()
        return token

    def remove_token(self, symbol: str) -> bool:
        """Remove custom token"""
        if symbol in self.custom_tokens:
            del self.custom_tokens[symbol]
            self.save_custom_tokens()
            return True
        return False

    def get_token(self, symbol: str) -> Optional[Token]:
        """Get token by symbol"""
        return self.all_tokens.get(symbol)


# Create global token manager instance
token_manager = TokenManager()

# Define initial trading pairs
TRADING_PAIRS = [
    TradingPair(
        base=token_manager.get_token("WETH"),
        quote=token_manager.get_token("USDT"),
        min_amount=0.1,
        max_amount=10
    ),
    TradingPair(
        base=token_manager.get_token("WETH"),
        quote=token_manager.get_token("USDC"),
        min_amount=0.1,
        max_amount=10
    ),
]