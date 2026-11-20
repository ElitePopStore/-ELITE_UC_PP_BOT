
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ContextTypes, filters
)

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = 6180671831

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("⚡ Instant Popularity", callback_data="instant")],
        [InlineKeyboardButton("🔥 Last Minute Popularity", callback_data="last")],
        [InlineKeyboardButton("📦 My Orders", callback_data="orders")],
        [InlineKeyboardButton("💬 Contact Admin", callback_data="support")]
    ]
    await update.message.reply_text(
        "🎮 ELITE UC & PP STORE\n\nWelcome! Select your service:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    if q.data in ["instant", "last"]:
        context.user_data["service"] = q.data
        await q.edit_message_text(
            "Enter your PUBG UID:"
        )
    elif q.data == "orders":
        await q.edit_message_text("📦 Your orders will appear here.")
    elif q.data == "support":
        await q.edit_message_text("💬 Contact our store admin.")

async def messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if "uid" not in context.user_data:
        context.user_data["uid"] = text
        keyboard = [
            [InlineKeyboardButton("USDT", callback_data="usdt")],
            [InlineKeyboardButton("Easypaisa", callback_data="easypaisa")],
            [InlineKeyboardButton("JazzCash", callback_data="jazzcash")]
        ]
        await update.message.reply_text(
            "Select payment method:",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text("Please upload your payment screenshot.")

async def payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    context.user_data["payment"] = q.data
    await q.edit_message_text(
        "Please send your payment screenshot."
    )

async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await context.bot.send_photo(
        chat_id=ADMIN_ID,
        photo=update.message.photo[-1].file_id,
        caption=f"New order!\nUser: {user.id}\nUID: {context.user_data.get('uid')}\nPayment: {context.user_data.get('payment')}\nService: {context.user_data.get('service')}"
    )
    await update.message.reply_text(
        "✅ Payment screenshot received. Admin will verify your order."
    )

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(payment, pattern="^(usdt|easypaisa|jazzcash)$"))
    app.add_handler(CallbackQueryHandler(menu))
    app.add_handler(MessageHandler(filters.PHOTO, photo))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, messages))
    app.run_polling()

if __name__ == "__main__":
    main()
