import telebot
from deep_translator import GoogleTranslator
from langdetect import detect

BOT_TOKEN = "8743715628:AAHvu9C84H-yWtrBR3_FuTg5CEkMt2iLGNE"

bot = telebot.TeleBot(BOT_TOKEN)


@bot.message_handler(func=lambda message: True, content_types=["text"])
def auto_translate_group(message):
    try:
        if message.from_user and message.from_user.is_bot:
            return

        if message.chat.type not in ["group", "supergroup"]:
            return

        text = (message.text or "").strip()
        if not text:
            return

        # Thử dịch sang EN
        translated_en = GoogleTranslator(source="auto", target="en").translate(text)

        # Nếu khác text gốc → nghĩa là text không phải tiếng Anh
        if translated_en.lower() != text.lower():
            label = "VI → EN"
            result = translated_en
        else:
            # Nếu giống → thử dịch sang VI
            translated_vi = GoogleTranslator(source="auto", target="vi").translate(text)
            if translated_vi.lower() != text.lower():
                label = "EN → VI"
                result = translated_vi
            else:
                return  # không dịch được thì bỏ qua

        sender = message.from_user.first_name or "User"

        bot.send_message(
            message.chat.id,
            f"[{label}] {sender}: {result}"
        )

    except Exception as e:
        print("Lỗi:", e)


print("Bot đang chạy...")
bot.infinity_polling()