# telegram_handler.py
import telebot
from typing import Optional


class TelegramHandler:
    def __init__(self, token: str, chat_id: str):
        self.bot = telebot.TeleBot(token)
        self.chat_id = chat_id
        self.last_message_id = None

    def send_initial_message(self) -> None:
        """Send initial message and store its ID for future updates"""
        message = "🤖 Arbitrage Bot Started\n\nMonitoring prices..."
        sent_message = self.bot.send_message(self.chat_id, message)
        self.last_message_id = sent_message.message_id

    def update_message(self, prices_text: str, opportunities_text: Optional[str] = None) -> None:
        """Update the existing message with new prices and opportunities"""
        message = "🤖 Arbitrage Monitor\n\n"
        message += prices_text

        if opportunities_text:
            message += "\n\n💰 Arbitrage Opportunities:\n"
            message += opportunities_text

        try:
            self.bot.edit_message_text(
                message,
                chat_id=self.chat_id,
                message_id=self.last_message_id,
                parse_mode='Markdown'
            )
        except Exception as e:
            print(f"Error updating Telegram message: {str(e)}")
            # If edit fails, send a new message
            self.send_initial_message()