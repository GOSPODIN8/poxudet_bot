import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage

import config
import database as db
from handlers import start, survey, payments, content_admin, manual_post, fallback
from scheduler import setup_scheduler


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
    dp.include_router(content_admin.router)
    dp.include_router(manual_post.router)
    dp.include_router(fallback.router)  # обязательно последним

    if config.GEMINI_API_KEY:
        setup_scheduler(bot)
    else:
        logging.warning("GEMINI_API_KEY не задан — автопостинг контента отключён.")

    logging.info("Бот запущен, жду сообщения...")
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
