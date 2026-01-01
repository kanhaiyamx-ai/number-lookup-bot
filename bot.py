import telebot
import requests
import time
import os
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# ================= CONFIG =================
BOT_TOKEN = os.getenv("BOT_TOKEN")

CHANNEL_ID = -1003636897874
CHANNEL_INVITE = "https://t.me/+lrUh5WrPCJM5OTM1"
API_URL = "https://ownerjii-api-ayno.vercel.app/api/info"

COOLDOWN = 10
USER_TIME = {}

bot = telebot.TeleBot(BOT_TOKEN)

# ================= HELPERS =================
def is_joined(user_id):
    try:
        m = bot.get_chat_member(CHANNEL_ID, user_id)
        return m.status in ["member", "administrator", "creator"]
    except:
        return False

def join_keyboard():
    kb = InlineKeyboardMarkup()
    kb.add(InlineKeyboardButton("✅ Join Telegram Channel", url=CHANNEL_INVITE))
    return kb

def result_keyboard():
    kb = InlineKeyboardMarkup(row_width=1)
    kb.add(
        InlineKeyboardButton("🔍 Search Another Number", callback_data="again"),
        InlineKeyboardButton("⬅️ Back", callback_data="back")
    )
    return kb

def disable_buttons(msg):
    try:
        bot.edit_message_reply_markup(msg.chat.id, msg.message_id, reply_markup=None)
    except:
        pass

def clean_address(addr):
    if not addr:
        return None
    addr = addr.replace("!", " ")
    addr = " ".join(addr.split())
    words = addr.split()
    out = []
    for w in words:
        if not out or out[-1].lower() != w.lower():
            out.append(w)
    return " ".join(out)

# ================= START =================
@bot.message_handler(commands=["start"])
def start(msg):
    bot.send_message(
        msg.chat.id,
        (
            "👋 <b>Welcome to Number Lookup Express</b>\n\n"
            "📞 <i>Send a phone number to find available details quickly and easily.</i>\n\n"
            "<b>Requirements</b>\n"
            "<i>• Digits only</i>\n"
            "<i>• Length 10–13 digits</i>\n\n"
            "<b>Example</b>\n"
            "<code>7982252786</code>\n\n"
            "━━━━━━━━━━━━━━\n"
            "<i>Need help or facing an issue?</i>\n"
            "<b><i>DM @KILL4R_UR</i></b>"
        ),
        parse_mode="HTML"
    )

# ================= CALLBACKS =================
@bot.callback_query_handler(func=lambda c: c.data == "again")
def again(c):
    bot.answer_callback_query(c.id)
    disable_buttons(c.message)
    start(c.message)

@bot.callback_query_handler(func=lambda c: c.data == "back")
def back(c):
    bot.answer_callback_query(c.id)
    disable_buttons(c.message)
    start(c.message)

# ================= MAIN =================
@bot.message_handler(func=lambda m: True)
def lookup(msg):
    chat_id = msg.chat.id
    user_id = msg.from_user.id
    text = msg.text.strip()

    if not is_joined(user_id):
        bot.send_message(
            chat_id,
            (
                "🔒 <b>One-Step Access Required</b>\n\n"
                "<i>To use</i> <b>Number Lookup Express</b>, <i>please join our Telegram channel once.</i>\n\n"
                "<i>After joining, send the number again</i> <b>and the tool will work instantly.</b>\n\n"
                "<i>👇 Tap the button below to join</i>"
            ),
            reply_markup=join_keyboard(),
            parse_mode="HTML"
        )
        return

    now = time.time()
    if now - USER_TIME.get(user_id, 0) < COOLDOWN:
        bot.send_message(chat_id, "⏳ Please wait a few seconds.")
        return
    USER_TIME[user_id] = now

    if not text.isdigit() or not (10 <= len(text) <= 13):
        bot.send_message(chat_id, "❌ Please send a valid phone number.")
        return

    loading = bot.send_message(
        chat_id,
        "🔍 <b>Searching number details…</b>\n<i>Please wait a moment</i>",
        parse_mode="HTML"
    )

    try:
        res = requests.get(API_URL, params={"number": text}, timeout=10).json()
    except:
        bot.delete_message(chat_id, loading.message_id)
        bot.send_message(chat_id, "<b>Service error. Try again later.</b>", parse_mode="HTML")
        return

    records = res.get("result", {}).get("result")
    if not isinstance(records, list) or not records:
        bot.delete_message(chat_id, loading.message_id)
        bot.send_message(chat_id, "<b>No data found for this number.</b>", parse_mode="HTML")
        return

    r = records[0]
    address = clean_address(r.get("address"))

    reply = (
        "📊 <b>Number Lookup Result</b>\n\n"
        f"👤 <b>Name</b> <i>{r.get('name')}</i>\n"
        + (f"👨 <b>Father</b> <i>{r.get('father_name')}</i>\n" if r.get("father_name") else "")
        + (f"📱 <b>Mobile</b> <i>{r.get('mobile')}</i>\n" if r.get("mobile") else "")
        + (f"📞 <b>Alternate</b> <i>{r.get('alt_mobile')}</i>\n" if r.get("alt_mobile") else "")
        + "\n"
        + (f"📍 <b>Address</b>\n<i>{address}</i>\n\n" if address else "")
        + (f"📡 <b>Circle</b> <i>{r.get('circle')}</i>\n\n" if r.get("circle") else "")
        + "━━━━━━━━━━━━━━\n"
        "<i>🔍 Powered by Number Lookup Express</i>"
    )

    bot.delete_message(chat_id, loading.message_id)
    bot.send_message(chat_id, reply, parse_mode="HTML", reply_markup=result_keyboard())

# ================= RUN =================
print("✅ Bot running")
bot.remove_webhook()
bot.infinity_polling()
