import logging
import os
import sys

from dotenv import load_dotenv
from telegram import Update
from telegram.error import InvalidToken, NetworkError
from telegram.ext import Application, CommandHandler, ContextTypes

from advice import TIPS

load_dotenv()
logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "Привет! Я Climate Nearby Bot — помогу найти экологические советы "
            "и сообщить о проблемах в городе.\n\n"
            "Используйте /tips для советов, /map для карты или /help для справки."
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        await update.message.reply_text(
            "Доступные команды:\n"
            "/start — начать работу\n"
            "/help — показать справку\n"
            "/tips — получить советы по экологии и жаре\n"
            "/map — открыть карту сообщений (API должен быть запущен)"
        )


async def tips(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        text = "Экологические советы:\n" + "\n".join(
            f"• {tip['title']}: {tip['text']}" for tip in TIPS
        )
        await update.message.reply_text(text)


async def map_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message:
        base_url = os.getenv("PUBLIC_BASE_URL", "http://127.0.0.1:8000").rstrip("/")
        await update.message.reply_text(f"Карта сообщений: {base_url}/map")


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Ошибка при обработке обновления", exc_info=context.error)


def main() -> int:
    token = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()
    if not token:
        print(
            "Ошибка: не задан TELEGRAM_BOT_TOKEN. Заполните его в файле .env.",
            file=sys.stderr,
        )
        return 1

    try:
        application = (
            Application.builder()
            .token(token)
            .connect_timeout(30)
            .read_timeout(30)
            .write_timeout(30)
            .pool_timeout(30)
            .build()
        )
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        application.add_handler(CommandHandler("tips", tips))
        application.add_handler(CommandHandler("map", map_command))
        application.add_error_handler(error_handler)

        print("Бот запущен. Для остановки нажмите Ctrl+C.")
        application.run_polling(drop_pending_updates=True)
        return 0
    except InvalidToken:
        print(
            "Ошибка: Telegram отклонил токен. Проверьте TELEGRAM_BOT_TOKEN в .env.",
            file=sys.stderr,
        )
        return 1
    except NetworkError as error:
        print(
            f"Не удалось подключиться к Telegram: {error}\n"
            "Проверьте интернет, доступ к api.telegram.org и настройки прокси/VPN.",
            file=sys.stderr,
        )
        return 1
    except KeyboardInterrupt:
        print("\nБот остановлен.")
        return 0
    except Exception as error:
        logger.exception("Не удалось запустить бота")
        print(f"Ошибка запуска: {error}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
