# telegram_handler.py
import telebot
from typing import Optional, Dict
from tokens import token_manager
from users import user_manager
import threading
from web3 import Web3


class TelegramHandler:
    def __init__(self, token: str):
        self.bot = telebot.TeleBot(token)
        self.user_pairs = set()
        self.web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/YOUR_INFURA_KEY'))
        # Dictionary to store last message ID for each user
        self.user_messages: Dict[str, int] = {}
        self.setup_handlers()

    def setup_handlers(self):
        @self.bot.message_handler(commands=['start'])
        def handle_start(message):
            chat_id = str(message.chat.id)
            user_manager.add_user(chat_id)
            welcome_text = (
                "👋 *Welcome to Arbitrage Monitor Bot!*\n\n"
                "You will now receive price updates and arbitrage opportunities.\n\n"
                "Use /help to see available commands."
            )
            self.bot.reply_to(message, welcome_text, parse_mode='Markdown')

        @self.bot.message_handler(commands=['help'])
        def handle_help(message):
            help_text = (
                "👋 *Available Commands:*\n\n"
                "*Token Management:*\n"
                "• `/add_token SYMBOL ADDRESS DECIMALS` - Add new token\n"
                "• `/remove_token SYMBOL` - Remove custom token\n"
                "• `/list_tokens` - Show available tokens\n"
                "• `/token_info SYMBOL` - Show token details\n\n"
                "*Pair Management:*\n"
                "• `/add_pair TOKEN1 TOKEN2` - Add trading pair\n"
                "• `/remove_pair PAIR` - Remove pair\n"
                "• `/pairs` - Show monitored pairs\n\n"
                "*Examples:*\n"
                "• `/add_token PEPE 0x6982508145454Ce325dDbE47a25d4ec3d2311933 18`\n"
                "• `/add_pair PEPE USDT`"
            )
            self.bot.reply_to(message, help_text, parse_mode='Markdown')

        @self.bot.message_handler(commands=['add_token'])
        def handle_add_token(message):
            try:
                parts = message.text.split()
                if len(parts) != 4:
                    raise ValueError("Wrong number of arguments")

                _, symbol, address, decimals = parts
                address = self.web3.to_checksum_address(address)
                decimals = int(decimals)

                if not self.web3.is_address(address):
                    self.bot.reply_to(message, "❌ Invalid Ethereum address!")
                    return

                if not (0 <= decimals <= 18):
                    self.bot.reply_to(message, "❌ Decimals must be between 0 and 18!")
                    return

                token = token_manager.add_token(symbol, address, decimals)
                response = (
                    f"✅ Token added successfully!\n\n"
                    f"*Symbol:* `{token.symbol}`\n"
                    f"*Address:* `{token.address}`\n"
                    f"*Decimals:* `{token.decimals}`\n\n"
                    f"You can now create pairs with this token using:\n"
                    f"`/add_pair {token.symbol} USDT`"
                )
                self.bot.reply_to(message, response, parse_mode='Markdown')

            except Exception as e:
                self.bot.reply_to(message, f"❌ Error: {str(e)}")

        @self.bot.message_handler(commands=['list_tokens'])
        def handle_list_tokens(message):
            tokens = token_manager.all_tokens

            def format_token(token):
                return f"• *{token.symbol}* - `{token.address[:8]}...{token.address[-6:]}`"

            default_tokens = [t for t in tokens.values() if t.symbol in token_manager.default_tokens]
            custom_tokens = [t for t in tokens.values() if t.symbol in token_manager.custom_tokens]

            text = "*Available Tokens:*\n\n"

            if default_tokens:
                text += "*Default Tokens:*\n"
                text += "\n".join(format_token(t) for t in default_tokens)

            if custom_tokens:
                text += "\n\n*Custom Tokens:*\n"
                text += "\n".join(format_token(t) for t in custom_tokens)

            if not custom_tokens:
                text += "\n\nNo custom tokens added yet."
                text += "\nUse `/add_token SYMBOL ADDRESS DECIMALS` to add."

            self.bot.reply_to(message, text, parse_mode='Markdown')

        @self.bot.message_handler(commands=['add_pair'])
        def handle_add_pair(message):
            try:
                _, token1, token2 = message.text.split()

                base_token = token_manager.get_token(token1)
                quote_token = token_manager.get_token(token2)

                if not base_token or not quote_token:
                    self.bot.reply_to(message,
                                      "❌ One or both tokens not found! Use /list_tokens to see available tokens.")
                    return

                pair_str = f"{token1}-{token2}"
                self.user_pairs.add(pair_str)

                response = (
                    f"✅ Added pair *{pair_str}* to monitoring\n\n"
                    f"*Base Token:* {base_token.symbol}\n"
                    f"*Quote Token:* {quote_token.symbol}"
                )
                self.bot.reply_to(message, response, parse_mode='Markdown')

            except ValueError:
                self.bot.reply_to(message, "❌ Use format: `/add_pair TOKEN1 TOKEN2`", parse_mode='Markdown')

        @self.bot.message_handler(commands=['pairs'])
        def handle_pairs(message):
            if not self.user_pairs:
                response = (
                    "*No custom pairs added*\n\n"
                    "Add pairs using:\n"
                    "`/add_pair TOKEN1 TOKEN2`"
                )
            else:
                response = "*Monitored Pairs:*\n\n"
                for pair in sorted(self.user_pairs):
                    response += f"• *{pair}*\n"

            self.bot.reply_to(message, response, parse_mode='Markdown')

    def run(self):
        """Start the bot in a separate thread"""

        def polling():
            print("Starting Telegram bot polling...")
            self.bot.polling(none_stop=True, interval=1)

        polling_thread = threading.Thread(target=polling)
        polling_thread.daemon = True
        polling_thread.start()

    def update_prices(self, prices_text: str, opportunities_text: Optional[str] = None):
        """Update price messages for all users"""
        message = f"{prices_text}"
        if opportunities_text:
            message += f"\n\n{opportunities_text}"

        for chat_id in user_manager.get_all_users():
            try:
                # If user already has a message, update it
                if chat_id in self.user_messages:
                    try:
                        self.bot.edit_message_text(
                            chat_id=chat_id,
                            message_id=self.user_messages[chat_id],
                            text=message,
                            parse_mode='Markdown'
                        )
                    except telebot.apihelper.ApiException as e:
                        if "message is not modified" not in str(e).lower():
                            raise e
                # If not, send new message and store its ID
                else:
                    sent_msg = self.bot.send_message(
                        chat_id=chat_id,
                        text=message,
                        parse_mode='Markdown'
                    )
                    self.user_messages[chat_id] = sent_msg.message_id
            except Exception as e:
                print(f"Error updating prices for user {chat_id}: {e}")