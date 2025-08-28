from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Owner Telegram user ID
OWNER_ID =  7994709010

# Dictionary to store reply sessions (owner replying to which user)
reply_sessions = {}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Send me a message (text or photo) and I’ll forward it to the owner.")

# When a user (NOT owner) sends a text or photo
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id == OWNER_ID:
        return  # Ignore owner's own messages

    user = update.effective_user

    if update.message.text:  # Text message
        text = update.message.text
        msg_to_owner = f"📩 Message from @{user.username or 'NoUsername'} (ID: {user.id}):\n\n{text}"
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("💬 Reply", callback_data=f"reply:{user.id}:{user.username or 'NoUsername'}")]]
        )
        await context.bot.send_message(chat_id=OWNER_ID, text=msg_to_owner, reply_markup=keyboard)

    elif update.message.photo:  # Photo message
        photo = update.message.photo[-1].file_id
        caption = update.message.caption or ""
        msg_to_owner = f"📸 Photo from @{user.username or 'NoUsername'} (ID: {user.id}):\n{caption}"
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("💬 Reply", callback_data=f"reply:{user.id}:{user.username or 'NoUsername'}")]]
        )
        await context.bot.send_photo(chat_id=OWNER_ID, photo=photo, caption=msg_to_owner, reply_markup=keyboard)

    # Confirm to user
    await update.message.reply_text("✅ Your message has been sent to the owner.")

# Handle button press (when owner clicks reply)
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("reply:"):
        return

    parts = query.data.split(":")
    user_id = int(parts[1])
    username = parts[2]

    # Save reply session
    reply_sessions[OWNER_ID] = user_id

    await query.message.reply_text(
        f"✍️ You are replying to @{username} (ID: {user_id}).\nSend any message (text/photo/sticker) and I’ll deliver it."
    )

# Forward owner's reply back to user
async def forward_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != OWNER_ID:
        return  # Only allow owner to use this

    if OWNER_ID not in reply_sessions:
        return await update.message.reply_text("⚠️ Please click 'Reply' on a user message first.")

    user_id = reply_sessions[OWNER_ID]

    # Forward text
    if update.message.text:
        await context.bot.send_message(chat_id=user_id, text=f"📬 Reply from owner:\n{update.message.text}")
        await update.message.reply_text("✅ Message sent.")

    # Forward photo
    elif update.message.photo:
        photo = update.message.photo[-1].file_id
        caption = f"📬 Reply from owner:\n{update.message.caption or ''}"
        await context.bot.send_photo(chat_id=user_id, photo=photo, caption=caption)
        await update.message.reply_text("✅ Photo sent.")

    # Forward stickers, documents, etc.
    elif update.message.sticker:
        await context.bot.send_sticker(chat_id=user_id, sticker=update.message.sticker.file_id)
        await update.message.reply_text("✅ Sticker sent.")
    elif update.message.document:
        await context.bot.send_document(chat_id=user_id, document=update.message.document.file_id, caption="📬 Reply from owner")
        await update.message.reply_text("✅ Document sent.")
    else:
        await update.message.reply_text("⚠️ This file type is not supported yet.")

def main():
    app = Application.builder().token("8293205720:AAGPGvxkXJmy_-zj0rYSjFruKTba-1bVit8").build()

    app.add_handler(CommandHandler("start", start))

    # Users ke liye handler (OWNER_ID exclude)
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND, handle_message))

    # Callback for reply button
    app.add_handler(CallbackQueryHandler(button_handler))

    # Owner ke replies ke liye alag handler
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, forward_reply))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
