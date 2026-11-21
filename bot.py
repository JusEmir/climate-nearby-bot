import os

from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

load_dotenv()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Привет! Я Climate Nearby Bot — помогу найти экологические советы, "
        "узнать о локальных мероприятиях и сообщить о проблемах в городе.\n\n"
        "Напишите /help, чтобы посмотреть доступные команды."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Доступные команды:\n"
        "/start — начать работу\n"
        "/help — показать справку\n"
        "/tips — получить советы по жаре и экологии"
    )


async def tips(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Несколько базовых советов:\n"
        "• Берегите воду и используйте кондиционер экономно.\n"
        "• В жару избегайте длительного нахождения на солнце.\n"
        "• Используйте общественный транспорт или передвижение пешком.\n"
        "• Выключайте ненужные электроприборы."
    )


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError("Укажите TELEGRAM_BOT_TOKEN в файле .env")

    application = Application.builder().token(token).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("tips", tips))

    print("Бот запущен")
    application.run_polling()


if __name__ == "__main__":
    main()
