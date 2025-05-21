import logging
import asyncio
import os
import nest_asyncio
from telegram import Update, ChatPermissions, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (ApplicationBuilder, MessageHandler, filters,
                          CommandHandler, ContextTypes, ChatMemberHandler, CallbackQueryHandler)

# === CONFIGURATION ===
BOT_TOKEN = "7496477077:AAFU7uiQbaZZC5GCZ0Yk-5Srz9Fif6Qmqaw"
BANNED_WORDS_FILE = "banned_words.txt.txt"
ADMINS_FILE = "admins.txt.txt"
WELCOME_TEXT = "Добро пожаловать, {name}! Ознакомьтесь с правилами: https://t.me/f1ves_chat/1816/2151 и нажмите кнопку ниже."

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === UTILITIES ===
def load_banned_words():
    if os.path.exists(BANNED_WORDS_FILE):
        with open(BANNED_WORDS_FILE, 'r', encoding='utf-8') as f:
            return [line.strip().lower() for line in f if line.strip()]
    return []

def save_banned_words(words):
    with open(BANNED_WORDS_FILE, 'w', encoding='utf-8') as f:
        for word in sorted(set(words)):
            f.write(word + '\n')

def load_admins():
    if os.path.exists(ADMINS_FILE):
        with open(ADMINS_FILE, 'r') as f:
            return [int(line.strip()) for line in f if line.strip().isdigit()]
    return []

async def get_chat_owner_id(chat):
    admins = await chat.get_administrators()
    for admin in admins:
        if admin.status == "creator":
            return admin.user.id
    return None

async def check_permission(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    chat = update.effective_chat
    user = update.effective_user
    admins = await chat.get_administrators()
    admin_ids = [admin.user.id for admin in admins]
    owner_id = next((admin.user.id for admin in admins if admin.status == "creator"), None)
    if user.id in admin_ids or user.id == owner_id:
        return True
    await update.message.reply_text("❌ Аааа, хитрец! Низя!")
    return False

# === COMMANDS ===
async def command_addword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    owner_id = await get_chat_owner_id(update.effective_chat)
    if update.effective_user.id != owner_id:
        await update.message.reply_text("❌ Аааа, хитрец! Низя!")
        return
    if not context.args:
        await update.message.reply_text("❗ Укажите слово для добавления.")
        return
    word = context.args[0].lower()
    words = load_banned_words()
    if word in words:
        await update.message.reply_text("⚠️ Это слово уже в списке.")
    else:
        words.append(word)
        save_banned_words(words)
        await update.message.reply_text(f"✅ Слово '{word}' добавлено в фильтр.")

async def command_delword(update: Update, context: ContextTypes.DEFAULT_TYPE):
    owner_id = await get_chat_owner_id(update.effective_chat)
    if update.effective_user.id != owner_id:
        await update.message.reply_text("❌ Аааа, хитрец! Низя!.")
        return
    if not context.args:
        await update.message.reply_text("❗ Укажите слово для удаления.")
        return
    word = context.args[0].lower()
    words = load_banned_words()
    if word not in words:
        await update.message.reply_text("⚠️ Этого слова нет в списке.")
    else:
        words.remove(word)
        save_banned_words(words)
        await update.message.reply_text(f"🗑️ Слово '{word}' удалено из фильтра.")

async def command_listwords(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_permission(update, context):
        return
    words = load_banned_words()
    if words:
        await update.message.reply_text("📃 Список запрещённых слов:\n" + "\n".join(words))
    else:
        await update.message.reply_text("📃 Список пуст.")

async def command_rules(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_permission(update, context):
        return
    await update.message.reply_text("Правила группы: https://t.me/f1ves_chat/1816/2151")

async def command_topics(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await check_permission(update, context):
        return
    thread_id = update.message.message_thread_id
    if thread_id:
        await update.message.reply_text(f"🧵 ID этой темы: {thread_id}")
    else:
        await update.message.reply_text("❗ Эта группа не использует темы или вы пишете вне темы.")

# === MESSAGE FILTER ===
async def check_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.effective_message
    user = update.effective_user
    chat = update.effective_chat

    if not message or not message.text:
        return

    admins = await chat.get_administrators()
    admin_ids = [admin.user.id for admin in admins]
    if user.id in admin_ids:
        return

    banned_words = load_banned_words()
    text = message.text.lower()
    if any(word in text for word in banned_words):
        try:
            await message.delete()
            await context.bot.send_message(
                chat_id=chat.id,
                text=f"⚠️ {user.full_name}, ваше сообщение удалено за нарушение правил."
            )
            await context.bot.restrict_chat_member(
                chat_id=chat.id,
                user_id=user.id,
                permissions=ChatPermissions(can_send_messages=False),
                until_date=asyncio.get_event_loop().time() + 86400
            )
        except Exception as e:
            logger.warning(f"Ошибка при удалении или ограничении: {e}")

# === MAIN ENTRY ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("addword", command_addword))
    app.add_handler(CommandHandler("delword", command_delword))
    app.add_handler(CommandHandler("listwords", command_listwords))
    app.add_handler(CommandHandler("rules", command_rules))
    app.add_handler(CommandHandler("topics", command_topics))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_message))

    print("Бот запущен...")
    app.run_polling()

if __name__ == '__main__':
    nest_asyncio.apply()
    main()
