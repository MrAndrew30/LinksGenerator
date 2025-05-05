import asyncio
import os
import logging
from aiogram import Bot, Dispatcher, types
from dotenv import dotenv_values
import handler_commands


async def main():
    # Конфигурация бота - токены для VK_API, Google, Telegram
    logger.info("Получение значений из виртуального окружения")
    config = dotenv_values(".env")

    logger.info("Запуск бота")
    bot = Bot(token=config["BOT_TOKEN"])
    dp = Dispatcher()
    dp.include_router(handler_commands.router)

    # Пропускаем все накопленные входящие и запускаем бота
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename="py_log.log")
    logger = logging.getLogger(__name__)
    asyncio.run(main())
