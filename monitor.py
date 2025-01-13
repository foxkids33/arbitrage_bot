# monitor.py
from typing import Dict, List, Optional, Tuple
import time
from datetime import datetime
from web3 import Web3
from config import MIN_PROFIT_USD, CHECK_INTERVAL, DEFAULT_AMOUNT
from tokens import TradingPair, token_manager
from exchanges import Exchange
from telegram_handler import TelegramHandler


class PriceMonitor:
    def __init__(self, web3: Web3, exchanges: Dict[str, Exchange],
                 pairs: List[TradingPair], telegram: TelegramHandler):
        self.web3 = web3
        self.exchanges = exchanges
        self.default_pairs = pairs
        self.telegram = telegram
        self.available_pairs = self._check_available_pairs(pairs)
        self.last_update_time = None

    def _check_available_pairs(self, pairs: List[TradingPair]) -> Dict[str, List[TradingPair]]:
        """Check which pairs are available on each exchange"""
        available = {}
        for exchange_name, exchange in self.exchanges.items():
            available[exchange_name] = []
            for pair in pairs:
                if exchange.check_pair_exists(pair):
                    available[exchange_name].append(pair)
        return available

    def get_current_pairs(self) -> List[TradingPair]:
        """Get current pairs including user-added ones"""
        all_pairs = self.default_pairs.copy()

        # Add user pairs
        for pair_str in self.telegram.user_pairs:
            try:
                base_symbol, quote_symbol = pair_str.split('-')
                base_token = token_manager.get_token(base_symbol)
                quote_token = token_manager.get_token(quote_symbol)

                if base_token and quote_token:
                    new_pair = TradingPair(
                        base=base_token,
                        quote=quote_token,
                        min_amount=0.1,
                        max_amount=10
                    )
                    if new_pair not in all_pairs:
                        all_pairs.append(new_pair)
            except Exception as e:
                print(f"Error processing pair {pair_str}: {str(e)}")

        return all_pairs

    def monitor_prices(self):
        """Monitor prices continuously"""
        while True:
            try:
                current_pairs = self.get_current_pairs()
                self.available_pairs = self._check_available_pairs(current_pairs)

                all_prices = {}
                opportunities = []

                for pair in current_pairs:
                    pair_str = str(pair)
                    prices = {}

                    for exchange_name, exchange in self.exchanges.items():
                        if pair in self.available_pairs[exchange_name]:
                            price = exchange.get_price(pair, DEFAULT_AMOUNT)
                            if price:
                                prices[exchange_name] = price

                    if len(prices) >= 2:
                        all_prices[pair_str] = prices

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

                # Format and broadcast messages
                prices_text = self._format_prices(all_prices)
                opportunities_text = self._format_opportunities(opportunities)
                self.telegram.update_prices(prices_text, opportunities_text)

                time.sleep(CHECK_INTERVAL)

            except Exception as e:
                print(f"Error in price monitoring: {str(e)}")
                time.sleep(CHECK_INTERVAL)

    def _format_prices(self, prices: Dict[str, Dict[str, float]]) -> str:
        current_time = datetime.now().strftime("%H:%M:%S")

        if not prices:
            return f"📊 No price data available\nLast update: {current_time}"

        text = f"📊 *Current Prices* (Updated: {current_time})\n"

        for pair_str, pair_prices in prices.items():
            text += f"\n💱 *{pair_str}*\n"
            for exchange, price in pair_prices.items():
                text += f"• _{exchange}_: `{price:.2f}`\n"
        return text

    def _format_opportunities(self, opportunities: List[Tuple]) -> Optional[str]:
        if not opportunities:
            return None

        text = "🔥 *Active Opportunities*\n"
        for pair, buy_ex, sell_ex, buy_price, sell_price, profit in opportunities:
            text += f"\n💰 *{pair}*\n"
            text += f"• Buy on _{buy_ex}_ at `{buy_price:.2f}`\n"
            text += f"• Sell on _{sell_ex}_ at `{sell_price:.2f}`\n"
            text += f"• Potential Profit: `${profit:.2f}`\n"
            text += f"• ROI: `{(profit / (buy_price * DEFAULT_AMOUNT) * 100):.2f}%`\n"
        return text