from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Owner Telegram user ID
OWNER_ID = 7347144999  

# When a user sends a message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    # Forward message to owner with username + ID
    msg_to_owner = f"📩 Message from @{user.username or 'NoUsername'} (ID: {user.id}):\n\n{text}"
    await context.bot.send_message(chat_id=OWNER_ID, text=msg_to_owner)

    # Confirm to user
    await update.message.reply_text("✅ Your message has been sent to the owner.")

# Owner replies to a user
async def reply_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return await update.message.reply_text("❌ You are not authorized.")

    try:
        user_id = int(context.args[0])
        reply_text = " ".join(context.args[1:])
        await context.bot.send_message(chat_id=user_id, text=f"📬 Reply from owner:\n{reply_text}")
        await update.message.reply_text("✅ Message sent successfully.")
    except Exception:
        await update.message.reply_text("⚠️ Usage: /reply <userid> <message>")

def main():
    # Your bot token
    app = Application.builder().token("8293205720:AAGPGvxkXJmy_-zj0rYSjFruKTba-1bVit8").build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CommandHandler("reply", reply_command))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
