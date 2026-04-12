import os
from flask import Flask, request
import telebot
from telebot import types
from deep_translator import GoogleTranslator

BOT_TOKEN = os.getenv("BOT_TOKEN")
RENDER_EXTERNAL_URL = os.getenv("RENDER_EXTERNAL_URL")

if not BOT_TOKEN:
    raise RuntimeError("Missing BOT_TOKEN")

bot = telebot.TeleBot(BOT_TOKEN)
app = Flask(__name__)

WEBHOOK_PATH = f"/webhook/{BOT_TOKEN}"
WEBHOOK_URL = f"{RENDER_EXTERNAL_URL}{WEBHOOK_PATH}" if RENDER_EXTERNAL_URL else None


def translate_text(text: str):
    text = (text or "").strip()
    if not text:
        return None

    try:
        translated_en = GoogleTranslator(source="auto", target="en").translate(text)
        if translated_en.lower() != text.lower():
            return "VI → EN", translated_en
    except Exception:
        pass

    try:
        translated_vi = GoogleTranslator(source="auto", target="vi").translate(text)
        if translated_vi.lower() != text.lower():
            return "EN → VI", translated_vi
    except Exception:
        pass

    return None


@bot.message_handler(content_types=["text"])
def handle_message(message: types.Message):
    if message.from_user and message.from_user.is_bot:
        return

    if message.chat.type not in ["group", "supergroup"]:
        return

    result = translate_text(message.text)
    if not result:
        return

    label, translated = result
    sender = message.from_user.first_name or "User"
    bot.send_message(message.chat.id, f"[{label}] {sender}: {translated}")


@app.route("/", methods=["GET"])
def healthcheck():
    return "Bot is running", 200


@app.route(WEBHOOK_PATH, methods=["POST"])
def webhook():
    if request.headers.get("content-type") == "application/json":
        json_str = request.get_data().decode("utf-8")
        update = types.Update.de_json(json_str)
        bot.process_new_updates([update])
        return "", 200
    return "Unsupported Media Type", 415


if __name__ == "__main__":
    if not RENDER_EXTERNAL_URL:
        raise RuntimeError("Missing RENDER_EXTERNAL_URL")

    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)

    port = int(os.getenv("PORT", "10000"))
    app.run(host="0.0.0.0", port=port)