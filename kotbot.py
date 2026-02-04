import os
from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
from dotenv import load_dotenv

# На сервере .env лежит в той же папке, что и скрипт
load_dotenv()

# Получаем токен
TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    exit("Ошибка: BOT_TOKEN не найден!")

# Используем относительные пути (актуально для Linux/PythonAnywhere)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PHOTO_PATH = os.path.join(BASE_DIR, "istockphoto-1385217969-612x612.jpg")
VOICE_PATH = os.path.join(BASE_DIR, "audio_2026-01-25_21-59-56.ogg")
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Напиши «Кот» или «Мяу».\n"
        "Отправь любой файл, и я его сохраню."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message

    if message.text:
        text = message.text.lower()
        if "кот" in text:
            if os.path.exists(PHOTO_PATH):
                with open(PHOTO_PATH, "rb") as photo:
                    await message.reply_photo(photo, caption="Вот фото кота!")
            else:
                await message.reply_text("Ошибка: фото не найдено на сервере.")
        
        elif "мяу" in text or "голосовое" in text:
            if os.path.exists(VOICE_PATH):
                with open(VOICE_PATH, "rb") as voice:
                    await message.reply_voice(voice, caption="Мяу-мяу!")
            else:
                await message.reply_text("Ошибка: аудио не найдено на сервере.")
        
        elif "оценка" in text:
            await message.reply_text("Новиков Кирилл ИСП23")
        else:
            await message.reply_text("Напишите «Кот» или «Мяу».")

    # Универсальная обработка файлов (документы, аудио, фото)
    elif message.document or message.audio or message.photo:
        try:
            if message.document:
                file = await context.bot.get_file(message.document.file_id)
                file_name = message.document.file_name
            elif message.audio:
                file = await context.bot.get_file(message.audio.file_id)
                file_name = message.audio.file_name or f"audio_{file.file_id}.mp3"
            elif message.photo:
                file = await context.bot.get_file(message.photo[-1].file_id)
                file_name = f"photo_{file.file_id}.jpg"

            save_path = os.path.join(DOWNLOAD_DIR, file_name)
            await file.download_to_drive(save_path)
            await message.reply_text(f"Сохранено: {file_name}")
        except Exception as e:
            await message.reply_text(f"Ошибка: {str(e)}")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        filters.TEXT | filters.Document.ALL | filters.AUDIO | filters.PHOTO,
        handle_message
    ))
    print("Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()
