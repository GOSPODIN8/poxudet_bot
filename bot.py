import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config
import database as db
from handlers import start, survey, payments


async def main():
    logging.basicConfig(level=logging.INFO)

    if not config.BOT_TOKEN:
        raise RuntimeError(
            "Не задан BOT_TOKEN. Добавь его в переменные окружения (см. README.md)."
        )

    db.init_db()

    bot = Bot(
        token=config.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)
    dp.include_router(survey.router)
    dp.include_router(payments.router)

    logging.info("Бот запущен, жду сообщения...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
