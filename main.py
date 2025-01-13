# main.py
from web3 import Web3
from config import INFURA_URL, ROUTERS, TELEGRAM_TOKEN
from tokens import TRADING_PAIRS
from exchanges import Exchange
from monitor import PriceMonitor
from telegram_handler import TelegramHandler
import time


def main():
    # Connect to Ethereum network
    web3 = Web3(Web3.HTTPProvider(INFURA_URL))

    if not web3.is_connected():
        print("❌ Failed to connect to Ethereum network")
        return

    print("✅ Connected to Ethereum network")

    try:
        # Initialize Telegram handler
        telegram = TelegramHandler(TELEGRAM_TOKEN)

        # Start Telegram bot
        telegram.run()

        # Give Telegram bot time to start
        time.sleep(2)

        # Initialize exchanges
        exchanges = {
            name: Exchange(web3, name, address)
            for name, address in ROUTERS.items()
        }

        # Create and start price monitor
        monitor = PriceMonitor(web3, exchanges, TRADING_PAIRS, telegram)

        # Print startup info
        print(f"\n🚀 Starting arbitrage bot...")
        print(f"📊 Monitoring {len(TRADING_PAIRS)} pairs across {len(exchanges)} exchanges")
        print("Bot is ready! Users can start bot with /start command")
        print("Press Ctrl+C to stop\n")

        # Start monitoring
        monitor.monitor_prices()

    except KeyboardInterrupt:
        print("\n👋 Stopping bot...")
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")


if __name__ == "__main__":
    main()