import datetime as dt
import os

from aiogram import Bot
from aiogram.types import FSInputFile
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

import config
import database as db
import keyboards as kb
from handlers.content_admin import generate_and_send_draft


async def publish_daily_post(bot: Bot) -> None:
    today = dt.date.today().isoformat()
    draft_row = db.get_approved_draft_for_date(today)

    if not draft_row:
        if config.ADMIN_ID:
            await bot.send_message(
                config.ADMIN_ID,
                "⚠️ На сегодня нет одобренного поста — публикация в бесплатный канал "
                "пропущена. Одобрите черновик заранее или запустите /post_today.",
            )
        return

    if not config.FREE_CHANNEL_ID:
        if config.ADMIN_ID:
            await bot.send_message(config.ADMIN_ID, "⚠️ Не задан FREE_CHANNEL_ID, публикация невозможна.")
        return

    caption = draft_row["text"]
    try:
        if draft_row["image_path"] and os.path.exists(draft_row["image_path"]):
            await bot.send_photo(
                config.FREE_CHANNEL_ID,
                FSInputFile(draft_row["image_path"]),
                caption=caption[:1024],
            )
        else:
            await bot.send_message(config.FREE_CHANNEL_ID, caption)

        await bot.send_message(
            config.FREE_CHANNEL_ID,
            config.DAILY_CTA_TEXT,
            reply_markup=kb.daily_post_cta_kb(),
        )
        db.set_draft_status(draft_row["id"], "published")

        if config.ADMIN_ID:
            await bot.send_message(config.ADMIN_ID, "✅ Пост дня опубликован в бесплатный канал.")
    except Exception as e:
        if config.ADMIN_ID:
            await bot.send_message(config.ADMIN_ID, f"⚠️ Не удалось опубликовать пост: {e}")


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    scheduler = AsyncIOScheduler(timezone=config.TIMEZONE)

    scheduler.add_job(
        generate_and_send_draft,
        CronTrigger(hour=config.PREPARE_HOUR, minute=config.PREPARE_MINUTE),
        args=[bot],
        id="prepare_daily_post",
        replace_existing=True,
    )

    scheduler.add_job(
        publish_daily_post,
        CronTrigger(hour=config.PUBLISH_HOUR, minute=config.PUBLISH_MINUTE),
        args=[bot],
        id="publish_daily_post",
        replace_existing=True,
    )

    scheduler.start()
    return scheduler
