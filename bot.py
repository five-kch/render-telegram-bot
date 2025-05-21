import logging
import asyncio
import os
import nest_asyncio
from telegram import Update, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (ApplicationBuilder, MessageHandler, filters,
                          CommandHandler, ContextTypes, ChatMemberHandler, CallbackQueryHandler)

# === CONFIGURATION ===
BOT_TOKEN = os.getenv("BOT_TOKEN")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === Заглушка для основного кода ===
def main():
    print("Бот запущен...")

if __name__ == "__main__":
    nest_asyncio.apply()
    main()
