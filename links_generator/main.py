import asyncio
import logging
from aiogram import Bot, Dispatcher
from pathlib import Path
import os
from dotenv import load_dotenv
import links_generator.handler_commands as handler_commands
from links_generator.googletables.worktables import GoogleSheetsManager
from links_generator.vk_api.vk_api import VKLinkManager
from links_generator.databases.databases import DatabaseManager

load_dotenv(override=True)

# Инициализация логгера в глобальной области
logger = logging.getLogger(__name__)

if os.environ.get('GENERATING_DOCS'):
    google_worker = None
else:
    google_worker = GoogleSheetsManager(os.getenv("GOOGLE_TABLE_ID"))

vk_api_worker = VKLinkManager(os.getenv("VK_TOKEN"))
db_worker = DatabaseManager("data/users.db")
admin_id = os.getenv("TG_ADMIN_ID")


async def async_main():
    """Асинхронная основная функция для запуска бота.

    Читает токен бота из переменных окружения, инициализирует бота и диспетчер,
    настраивает обработчики команд и запускает поллинг.

    Raises:
        ValueError: Если BOT_TOKEN не найден в переменных окружения или .env файле.
    """
    BOT_TOKEN = os.getenv("BOT_TOKEN")
    if not BOT_TOKEN:
        raise ValueError("BOT_TOKEN не задан в переменных окружения!")
    config = {"BOT_TOKEN": BOT_TOKEN}
    if not config.get("BOT_TOKEN"):
        logger.error("BOT_TOKEN не найден в .env файле!")
        raise ValueError("BOT_TOKEN не найден в .env файле!")

    logger.info("Запуск бота")
    bot = Bot(token=config["BOT_TOKEN"])
    dp = Dispatcher()
    handler_commands.setup(
        dp, google_worker, vk_api_worker, db_worker, admin_id)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


def main():
    """Синхронная точка входа для запуска бота.

    Настраивает базовую конфигурацию логирования и запускает асинхронную часть.
    """
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename="py_log.log"
    )
    asyncio.run(async_main())


if __name__ == "__main__":
    main()
