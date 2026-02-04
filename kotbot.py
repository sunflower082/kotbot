from telegram import Update
from telegram.ext import Application, MessageHandler, CommandHandler, filters, ContextTypes
import os
from dotenv import load_dotenv

# Загружаем переменные из файла .env
load_dotenv()

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    exit("Ошибка: BOT_TOKEN не найден в переменных окружения!")

# Получаем текущую папку, где лежит скрипт
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Универсальные пути
PHOTO_PATH = os.path.join(BASE_DIR, "istockphoto-1385217969-612x612.jpg")
VOICE_PATH = os.path.join(BASE_DIR, "audio_2026-01-25_21-59-56.ogg")
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")

os.makedirs(DOWNLOAD_DIR, exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает команду /start"""
    await update.message.reply_text(
        "Привет! Напиши «Кот», чтобы получить фото, или «Мяу», чтобы услышать голос кота!\n"
        "Отправь любой файл (MP3, DOCX, PDF и др.), и я сохраню его."
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Обрабатывает текстовые сообщения и файлы"""
    message = update.message

    if message.text:
        text = message.text.lower()
        if "кот" in text:
            try:
                with open(PHOTO_PATH, "rb") as photo:
                    await message.reply_photo(photo, caption="Вот фото кота!")
            except FileNotFoundError:
                await message.reply_text("Ошибка: фото не найдено на сервере.")
        elif "мяу" in text or "голосовое" in text:
            try:
                with open(VOICE_PATH, "rb") as voice:
                    await message.reply_voice(voice, caption="Мяу-мяу!")
            except FileNotFoundError:
                await message.reply_text("Ошибка: аудиофайл не найден на сервере.")
        elif "Оценка" in text:
            await message.reply_text("Новиков Кирилл ИСП23")
        else:
            await message.reply_text("Напишите «Кот» или «Мяу», чтобы получить файл.")

    elif message.document:
        file = await context.bot.get_file(message.document.file_id)
        file_name = message.document.file_name or "unknown_file"
        save_path = os.path.join(DOWNLOAD_DIR, file_name)
        try:
            await file.download_to_drive(save_path)
            await message.reply_text(f"Файл сохранён: {file_name}")
        except Exception as e:
            await message.reply_text(f"Ошибка при сохранении файла: {str(e)}")

    elif message.audio:
        file = await context.bot.get_file(message.audio.file_id)
        file_name = message.audio.file_name or f"audio_{message.audio.file_id}.mp3"
        save_path = os.path.join(DOWNLOAD_DIR, file_name)
        try:
            await file.download_to_drive(save_path)
            await message.reply_text(f"Аудио сохранено: {file_name}")
        except Exception as e:
            await message.reply_text(f"Ошибка при сохранении аудио: {str(e)}")

    elif message.photo:
        file = await context.bot.get_file(message.photo[-1].file_id)
        file_name = f"photo_{file.file_id}.jpg"
        save_path = os.path.join(DOWNLOAD_DIR, file_name)
        try:
            await file.download_to_drive(save_path)
            await message.reply_text(f"Фото сохранено: {file_name}")
        except Exception as e:
            await message.reply_text(f"Ошибка при сохранении фото: {str(e)}")


    else:
        await message.reply_text("Я принимаю только текстовые сообщения, документы, аудио и фото.")

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    
    app.add_handler(MessageHandler(
        filters.TEXT | filters.Document.ALL | filters.AUDIO | filters.PHOTO,
        handle_message
    ))
    
    app.run_polling()

if __name__ == "__main__":
    main()
