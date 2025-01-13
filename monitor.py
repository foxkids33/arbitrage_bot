# monitor.py
from typing import Dict, List, Optional, Tuple
import time
from web3 import Web3
from config import MIN_PROFIT_USD, CHECK_INTERVAL, DEFAULT_AMOUNT
from tokens import TradingPair
from exchanges import Exchange
from telegram_handler import TelegramHandler


class PriceMonitor:
    def __init__(self, web3: Web3, exchanges: Dict[str, Exchange],
                 pairs: List[TradingPair], telegram: TelegramHandler):
        self.web3 = web3
        self.exchanges = exchanges
        self.pairs = pairs
        self.telegram = telegram
        self.available_pairs = self._check_available_pairs()

    def _check_available_pairs(self) -> Dict[str, List[TradingPair]]:
        """Check which pairs are available on each exchange"""
        available = {}
        for exchange_name, exchange in self.exchanges.items():
            available[exchange_name] = []
            for pair in self.pairs:
                if exchange.check_pair_exists(pair):
                    available[exchange_name].append(pair)
        return available

    def _format_prices_text(self, all_prices: Dict[str, Dict[str, float]]) -> str:
        """Format prices for Telegram message"""
        text = ""
        for pair_str, prices in all_prices.items():
            text += f"\n*{pair_str}*\n"
            for exchange, price in prices.items():
                text += f"_{exchange}_: `{price:.2f}`\n"
        return text

    def _format_opportunities_text(self, opportunities: List[Tuple]) -> str:
        """Format opportunities for Telegram message"""
        if not opportunities:
            return "No arbitrage opportunities found"

        text = ""
        for pair, buy_exchange, sell_exchange, buy_price, sell_price, profit in opportunities:
            text += f"\n*{pair}*\n"
            text += f"Buy on _{buy_exchange}_ at `{buy_price:.2f}`\n"
            text += f"Sell on _{sell_exchange}_ at `{sell_price:.2f}`\n"
            text += f"Profit: `${profit:.2f}`\n"
        return text

    def monitor_prices(self):
        """Monitor prices continuously and update Telegram"""
        self.telegram.send_initial_message()

        while True:
            try:
                all_prices = {}
                opportunities = []

                for pair in self.pairs:
                    pair_str = str(pair)
                    prices = {}

                    # Get prices from exchanges that support this pair
                    for exchange_name, exchange in self.exchanges.items():
                        if pair in self.available_pairs[exchange_name]:
                            price = exchange.get_price(pair, DEFAULT_AMOUNT)
                            if price:
                                prices[exchange_name] = price

                    if len(prices) >= 2:
                        all_prices[pair_str] = prices

                        # Check for arbitrage
                        min_price = min(prices.values())
                        max_price = max(prices.values())
                        profit = (max_price - min_price) * DEFAULT_AMOUNT

                        if profit > MIN_PROFIT_USD:
                            min_exchange = [k for k, v in prices.items() if v == min_price][0]
                            max_exchange = [k for k, v in prices.items() if v == max_price][0]

                            opportunities.append((
                                pair_str,
                                min_exchange,
                                max_exchange,
                                min_price,
                                max_price,
                                profit
                            ))

                # Update Telegram message
                prices_text = self._format_prices_text(all_prices)
                opportunities_text = self._format_opportunities_text(opportunities)
                self.telegram.update_message(prices_text, opportunities_text)

                time.sleep(CHECK_INTERVAL)

            except Exception as e:
                print(f"Error in price monitoring: {str(e)}")
                time.sleep(CHECK_INTERVAL)