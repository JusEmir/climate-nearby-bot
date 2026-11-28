import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from advice import TIPS

load_dotenv()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я Climate Nearby Bot — помогу найти экологические советы "
        "и сообщить о проблемах в городе.\n\n"
        "Используйте /tips для советов, /map для карты или /help для справки."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start — начать работу\n"
        "/help — показать справку\n"
        "/tips — получить советы по экологии и жаре\n"
        "/map — открыть карту сообщений (нужен запущенный API)"
    )


async def tips(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = "Экологические советы:\n" + "\n".join(
        f"• {tip['title']}: {tip['text']}" for tip in TIPS
    )
    await update.message.reply_text(text)


async def map_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    base_url = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
    await update.message.reply_text(f"Карта сообщений: {base_url}/map")


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Укажите TELEGRAM_BOT_TOKEN в файле .env")

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("tips", tips))
    application.add_handler(CommandHandler("map", map_command))

    print("Бот запущен")
    application.run_polling()


if __name__ == "__main__":
    main()
