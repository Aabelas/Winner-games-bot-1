import os
import sqlite3
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    CallbackQueryHandler,
    MessageHandler,
    filters,
)

# ===== Database Setup =====
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        balance INTEGER DEFAULT 0
    )""")
    conn.commit()
    conn.close()

init_db()

# ====== Start Command ======
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("➡ Continue", callback_data="main_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(
        "🎉 Welcome to Winner Games!\n\nYour journey to fun and rewards starts here.",
        reply_markup=reply_markup
    )

# ====== Menu Handler ======
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "main_menu":
        keyboard = [
            [InlineKeyboardButton("🎮 Play Games", callback_data="play")],
            [InlineKeyboardButton("👤 Profile", callback_data="profile")],
            [InlineKeyboardButton("🎁 Rewards", callback_data="rewards")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text("🏠 Main Menu:", reply_markup=reply_markup)

    elif query.data == "profile":
        user_id = query.from_user.id
        username = query.from_user.username or query.from_user.first_name

        try:
            conn = sqlite3.connect("users.db")
            c = conn.cursor()
            c.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", (user_id, username))
            c.execute("SELECT balance FROM users WHERE user_id=?", (user_id,))
            result = c.fetchone()
            balance = result[0] if result else 0
            conn.commit()
        except Exception as e:
            balance = 0
            print("DB Error:", e)
        finally:
            conn.close()

        await query.edit_message_text(f"👤 Username: @{username}\n💰 Balance: {balance} coins")

    elif query.data == "play":
        await query.edit_message_text("🎮 Game section coming soon...")

    elif query.data == "rewards":
        await query.edit_message_text("🎁 Rewards will be available soon!")

# ====== Unknown Command Handler ======
async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Sorry, I didn't understand that command.")

# ====== Main ======
if __name__ == "__main__":
    BOT_TOKEN = "8368265957:AAFGd6E2YoUjP01W7Edu-c5uESX_RbwATpY"  # <-- Your Bot Token is here

    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    # Handle unknown commands gracefully
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    print("🤖 Bot is running...")
    app.run_polling()
