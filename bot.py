from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Multiple Owners
OWNER_IDS = [7347144999, 7994709010]  # <-- यहां अपने owners डालो

# Store reply sessions (which owner is replying to which user)
reply_sessions = {}

# /start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Hello! Send me a message (text/photo) and I’ll forward it to the owners.")

# Handle normal user messages
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user

    if update.message.text:
        text = update.message.text
        msg_to_owner = f"📩 Message from @{user.username or 'NoUsername'} (ID: {user.id}):\n\n{text}"
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("💬 Reply", callback_data=f"reply:{user.id}:{user.username or 'NoUsername'}")]]
        )
        for owner in OWNER_IDS:
            await context.bot.send_message(chat_id=owner, text=msg_to_owner, reply_markup=keyboard)

    elif update.message.photo:
        photo = update.message.photo[-1].file_id
        caption = update.message.caption or ""
        msg_to_owner = f"📸 Photo from @{user.username or 'NoUsername'} (ID: {user.id}):\n{caption}"
        keyboard = InlineKeyboardMarkup(
            [[InlineKeyboardButton("💬 Reply", callback_data=f"reply:{user.id}:{user.username or 'NoUsername'}")]]
        )
        for owner in OWNER_IDS:
            await context.bot.send_photo(chat_id=owner, photo=photo, caption=msg_to_owner, reply_markup=keyboard)

    await update.message.reply_text("✅ Your message has been sent to the owners.")

# Handle reply button press
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if not query.data.startswith("reply:"):
        return

    parts = query.data.split(":")
    user_id = int(parts[1])
    username = parts[2]

    # Save session for that specific owner
    reply_sessions[query.from_user.id] = user_id

    await query.message.reply_text(
        f"✍️ You are replying to @{username} (ID: {user_id}).\nNow send any message (text/photo/sticker)."
    )

# Forward reply from owner to user
async def forward_reply(update: Update, context: ContextTypes.DEFAULT_TYPE):
    owner_id = update.effective_user.id
    if owner_id not in OWNER_IDS:
        return

    if owner_id not in reply_sessions:
        return await update.message.reply_text("⚠️ Please click 'Reply' on a user message first.")

    user_id = reply_sessions[owner_id]

    # Text
    if update.message.text:
        await context.bot.send_message(chat_id=user_id, text=f"📬 Reply from owner:\n{update.message.text}")
        await update.message.reply_text("✅ Message sent to user.")

    # Photo
    elif update.message.photo:
        photo = update.message.photo[-1].file_id
        caption = f"📬 Reply from owner:\n{update.message.caption or ''}"
        await context.bot.send_photo(chat_id=user_id, photo=photo, caption=caption)
        await update.message.reply_text("✅ Photo sent to user.")

    # Sticker
    elif update.message.sticker:
        await context.bot.send_sticker(chat_id=user_id, sticker=update.message.sticker.file_id)
        await update.message.reply_text("✅ Sticker sent to user.")

    # Document
    elif update.message.document:
        await context.bot.send_document(chat_id=user_id, document=update.message.document.file_id, caption="📬 Reply from owner")
        await update.message.reply_text("✅ Document sent to user.")

    else:
        await update.message.reply_text("⚠️ This message type is not supported yet.")

def main():
    app = Application.builder().token("8293205720:AAGPGvxkXJmy_-zj0rYSjFruKTba-1bVit8").build()

    app.add_handler(CommandHandler("start", start))

    # Messages from normal users (exclude owners)
    app.add_handler(MessageHandler((filters.TEXT | filters.PHOTO) & ~filters.COMMAND & ~filters.User(OWNER_IDS), handle_message))

    # Reply button
    app.add_handler(CallbackQueryHandler(button_handler))

    # Messages from owners only
    app.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND & filters.User(OWNER_IDS), forward_reply))

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
