import json, os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CODES_FILE = "codes.json"

def load_codes():
    with open(CODES_FILE) as f: return json.load(f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send your code: e.g. EX-2025-001")

async def check_code(update: Update, context: ContextTypes.DEFAULT_TYPE):
    codes = load_codes()
    user_code = update.message.text.strip()
    if user_code in codes and not codes[user_code]["used"]:
        codes[user_code]["used"] = True
        with open(CODES_FILE, "w") as f: json.dump(codes, f, indent=2)
        await update.message.reply_text(f"✅ Code valid! Prize: {codes[user_code]['prize']}")
        if ADMIN_ID != 0:
            await context.bot.send_message(ADMIN_ID, f"Code used: {user_code} by {update.effective_user.id}")
    else:
        await update.message.reply_text("❌ Invalid or already used code.")

app = Application.builder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, check_code))
app.run_polling()
