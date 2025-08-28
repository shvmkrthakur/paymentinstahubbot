from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Owner Telegram user ID
OWNER_ID = 7347144999  

# Temporary storage: which user owner is replying to
reply_targets = {}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Send me a message and I’ll forward it to the owner.")

# When a user sends a message
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    text = update.message.text

    # Forward message to owner with username + ID
    msg_to_owner = f"📩 Message from @{user.username or 'NoUsername'} (ID: {user.id}):\n\n{text}"

    # Add "Reply" button
    keyboard = InlineKeyboardMarkup(
        [[InlineKeyboardButton("💬 Reply", callback_data=f"reply:{user.id}:{user.username or 'NoUsername'}")]]
    )

    await context.bot.send_message(chat_id=OWNER_ID, text=msg_to_owner, reply_markup=keyboard)

    # Confirm to user
    await update.message.reply_text("✅ Your message has been sent to the owner.")

# Handle button press
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("reply:"):
        return

    _, user_id, username = query.data.split(":")
    user_id = int(user_id)

    # Save target user
    reply_targets[OWNER_ID] = user_id

    await query.message.reply_text(
        f"📝 You are replying to @{username} (ID: {user_id}).\nJust type your message now."
    )

# When owner sends a message (check if he is replying to someone)
async def owner_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return

    if OWNER_ID in reply_targets:
        target_id = reply_targets[OWNER_ID]
        text = update.message.text

        # Send reply to user
        await context.bot.send_message(chat_id=target_id, text=f"📬 Reply from owner:\n{text}")

        # Confirm to owner
        await update.message.reply_text("✅ Reply sent.")

        # Remove target after one reply (optional)
        del reply_targets[OWNER_ID]

def main():
    # Your bot token
    app = Application.builder().token("8293205720:AAGPGvxkXJmy_-zj0rYSjFruKTba-1bVit8").build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, owner_message))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
