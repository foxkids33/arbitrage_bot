# exchanges.py
from web3 import Web3
from typing import Optional
from config import ROUTER_ABI
from tokens import TradingPair


class Exchange:
    def __init__(self, web3: Web3, name: str, router_address: str):
        self.web3 = web3
        self.name = name
        self.router = web3.eth.contract(
            address=web3.to_checksum_address(router_address),
            abi=ROUTER_ABI
        )

    def get_price(self, pair: TradingPair, amount: float) -> Optional[float]:
        """Get the price for a given trading pair and amount"""
        try:
            # Convert amount to wei (considering base token decimals)
            amount_in_wei = int(amount * 10 ** pair.base.decimals)

            # Create token path for the swap
            path = [
                self.web3.to_checksum_address(pair.base.address),
                self.web3.to_checksum_address(pair.quote.address)
            ]

            # Get amounts out
            amounts = self.router.functions.getAmountsOut(amount_in_wei, path).call()

            # Convert output amount from wei
            quote_amount = amounts[1] / (10 ** pair.quote.decimals)

            # Calculate price
            price = quote_amount / amount

            # Sanity check for WBTC prices (should be roughly between 20k and 100k)
            if pair.base.symbol == "WBTC" and (price < 20000 or price > 100000):
                print(f"Warning: Suspicious WBTC price from {self.name}: ${price:.2f}")
                return None

            return price

        except Exception as e:
            if "no data" in str(e):
                # This means the pair doesn't exist on this exchange
                print(f"Info: Pair {pair} not available on {self.name}")
            else:
                print(f"Error getting price from {self.name}: {str(e)}")
            return None

    def get_formatted_price(self, pair: TradingPair, amount: float) -> str:
        """Get formatted price string"""
        price = self.get_price(pair, amount)
        if price:
            return f"{self.name}: {price:.2f} {pair.quote.symbol}"
        return f"{self.name}: Not available"

    def check_pair_exists(self, pair: TradingPair) -> bool:
        """Check if a trading pair exists on this exchange"""
        try:
            # Try to get price for minimum amount
            price = self.get_price(pair, pair.min_amount)
            return price is not None
        except:
            return False