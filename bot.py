import logging
import asyncio
from datetime import timedelta, datetime
from telegram import Update, ChatPermissions
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ================= CONFIG =================
BOT_TOKEN = "8056017161:AAHtE3LeGjtKskiE2CMYyvJizs8T-FJ470M"  # Replace with your BotFather token
WORD_LIMIT = 200
SEND_WARNING = True
# ==========================================

logging.basicConfig(format="%(asctime)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

def is_admin(member) -> bool:
    return member.status in ("administrator", "creator")

async def limit_message_length(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    if not message or not message.text:
        return
    word_count = len(message.text.split())
    try:
        member = await update.effective_chat.get_member(message.from_user.id)
        if is_admin(member):
            return
    except Exception:
        pass
    if word_count > WORD_LIMIT:
        try:
            await message.delete()
            if SEND_WARNING:
                warn = await update.effective_chat.send_message(
                    f"⚠️ @{message.from_user.username or message.from_user.first_name}, "
                    f"your message had {word_count} words (limit {WORD_LIMIT})."
                )
                await asyncio.sleep(10)
                await warn.delete()
        except Exception as e:
            logger.error(f"Delete failed: {e}")

async def require_admin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    user = update.effective_user
    chat = update.effective_chat
    try:
        member = await chat.get_member(user.id)
        bot_member = await chat.get_member((await context.bot.get_me()).id)
        if not is_admin(member):
            await update.message.reply_text("❌ Only admins can use this command.")
            return False
        if not is_admin(bot_member):
            await update.message.reply_text("❌ I must be admin to do that.")
            return False
        return True
    except:
        await update.message.reply_text("Error checking admin status.")
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "👋 Hi! I'm Xpay Restricter Bot.\n"
        "I limit message length and help admins manage the group.\n\n"
        "Commands:\n"
        "/setlimit <num> — change limit\n"
        "/kick, /ban, /mute, /unmute — moderation\n"
        "/advertise <text> — post ad"
    )

async def setlimit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global WORD_LIMIT
    if not await require_admin(update, context): return
    args = update.message.text.split()
    if len(args) < 2 or not args[1].isdigit():
        await update.message.reply_text("Usage: /setlimit <number>")
        return
    WORD_LIMIT = int(args[1])
    await update.message.reply_text(f"✅ Word limit set to {WORD_LIMIT}")

async def kick(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context): return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user’s message with /kick.")
        return
    user_id = update.message.reply_to_message.from_user.id
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        await context.bot.unban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text("✅ User kicked.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def ban(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context): return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a user’s message with /ban.")
        return
    user_id = update.message.reply_to_message.from_user.id
    try:
        await context.bot.ban_chat_member(update.effective_chat.id, user_id)
        await update.message.reply_text("⛔ User banned.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def mute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context): return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message with /mute [minutes].")
        return
    user_id = update.message.reply_to_message.from_user.id
    args = update.message.text.split()
    minutes = int(args[1]) if len(args) > 1 and args[1].isdigit() else 60
    until = datetime.utcnow() + timedelta(minutes=minutes)
    try:
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            user_id,
            ChatPermissions(can_send_messages=False),
            until_date=until,
        )
        await update.message.reply_text(f"🔇 Muted for {minutes} minutes.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def unmute(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context): return
    if not update.message.reply_to_message:
        await update.message.reply_text("Reply to a message with /unmute.")
        return
    user_id = update.message.reply_to_message.from_user.id
    try:
        await context.bot.restrict_chat_member(
            update.effective_chat.id,
            user_id,
            ChatPermissions(can_send_messages=True),
        )
        await update.message.reply_text("🔊 User unmuted.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

async def advertise(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not await require_admin(update, context): return
    text = " ".join(update.message.text.split()[1:])
    if not text:
        await update.message.reply_text("Usage: /advertise <text>")
        return
    try:
        msg = await update.effective_chat.send_message(text)
        await msg.pin()
        await update.message.reply_text("📌 Advertisement posted and pinned.")
    except Exception as e:
        await update.message.reply_text(f"❌ Error: {e}")

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, limit_message_length))
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("setlimit", setlimit))
    app.add_handler(CommandHandler("kick", kick))
    app.add_handler(CommandHandler("ban", ban))
    app.add_handler(CommandHandler("mute", mute))
    app.add_handler(CommandHandler("unmute", unmute))
    app.add_handler(CommandHandler("advertise", advertise))
    print("🚀 Xpay Restricter Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
