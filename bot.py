import json
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

BOT_TOKEN = os.environ.get("BOT_TOKEN")
user_selection = {}
awaiting_account = {}

def load_codes():
    with open("codes.json", "r") as f:
        return json.load(f)

def save_codes(codes):
    with open("codes.json", "w") as f:
        json.dump(codes, f, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("$20", callback_data="20"), InlineKeyboardButton("$50", callback_data="50")],
        [InlineKeyboardButton("$100", callback_data="100"), InlineKeyboardButton("$200", callback_data="200")],
        [InlineKeyboardButton("$500", callback_data="500")]
    ]
    await update.message.reply_text("💰 Select amount to trade:", reply_markup=InlineKeyboardMarkup(keyboard))

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "connect":
        awaiting_account[query.from_user.id] = True
        await query.message.reply_text("🔗 CONNECT ACCOUNT TO WITHDRAW\n\nPlease send your trading account ID / wallet address:")
        return

    user_selection[query.from_user.id] = query.data
    await query.message.reply_text(f"You selected ${query.data}\nNow send your 20-digit code worth ${query.data}.")

async def check_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.from_user.id
    text = update.message.text.strip()

    # Step 3: User sent account ID
    if user_id in awaiting_account:
        amount = user_selection.get(user_id, "your")
        del awaiting_account[user_id]
        if user_id in user_selection:
            del user_selection[user_id]

        await update.message.reply_text(
            f"✅ ACCOUNT CONNECTED: {text}\n\n"
            f"💸 WITHDRAWAL PROCESSED!\n"
            f"Amount: ${amount}\n"
            f"Status: Sent to {text}\n\n"
            f"Thank you for trading with us!"
        )
        return

    # Step 2: Check code
    if user_id not in user_selection:
        await update.message.reply_text("Please type /start and select amount.")
        return

    selected = user_selection[user_id]
    codes = load_codes()

    if text in codes:
        if codes[text]["used"]:
            await update.message.reply_text("❌ Code already used")
            return
        if str(codes[text]["value"])!= str(selected):
            await update.message.reply_text(f"❌ This code is ${codes[text]['value']}, not ${selected}")
            return

        codes[text]["used"] = True
        save_codes(codes)

        keyboard = [[InlineKeyboardButton("🔗 Connect Account to Withdraw", callback_data="connect")]]
        await update.message.reply_text(
            f"✅ TRADED SUCCESSFULLY!\n\n💵 Amount: ${selected} Traded Successfully!",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    else:
        await update.message.reply_text("❌ Invalid 20-digit code")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_click))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_code))
    app.run_polling()

if __name__ == "__main__":
    main()
