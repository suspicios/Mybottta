from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# === CONFIG ===
BOT_TOKEN = "8056017161:AAHtE3LeGjtKskiE2CMYyvJizs8T-FJ470M"   # replace with your bot token
WORD_LIMIT = 200                    # set your custom word limit
SEND_WARNING = True                 # True = send warning message after deleting

# === FUNCTION TO HANDLE MESSAGES ===
async def limit_message_length(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return  # ignore non-text messages

    word_count = len(message.text.split())

    if word_count > WORD_LIMIT:
        try:
            await message.delete()
            if SEND_WARNING:
                await message.reply_text(
                    f"⚠️ Your message had {word_count} words — limit is {WORD_LIMIT}. "
                    "Please shorten your message."
                )
        except Exception as e:
            print(f"Error deleting message: {e}")

# === MAIN ===
def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handle all text messages
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, limit_message_length))

    print(f"✅ Bot running with word limit = {WORD_LIMIT}")
    app.run_polling()

if __name__ == "__main__":
    main()
