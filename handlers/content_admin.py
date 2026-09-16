import datetime as dt
import os

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import config
import database as db
import keyboards as kb
import content
from states import EditDraft

router = Router()


def _is_admin(user_id: int) -> bool:
    return config.ADMIN_ID and user_id == config.ADMIN_ID


def _monday_of_current_week() -> dt.date:
    today = dt.date.today()
    return today - dt.timedelta(days=today.weekday())


KIND_LABELS = {"daily": "Пост дня (бесплатный канал)", "weekly": "Программа недели (закрытый канал)"}


DAY_NAMES = ["mon", "tue", "wed", "thu", "fri", "sat", "sun"]


async def send_draft_preview(bot: Bot, draft_row) -> None:
    label = KIND_LABELS.get(draft_row["kind"], draft_row["kind"])
    caption = f"{label} · {draft_row['post_date']}\n\n{draft_row['text']}"
    if draft_row["image_path"] and os.path.exists(draft_row["image_path"]):
        await bot.send_photo(
            config.ADMIN_ID,
            FSInputFile(draft_row["image_path"]),
            caption=caption[:1024],
            reply_markup=kb.draft_approval_kb(draft_row["id"]),
        )
    else:
        await bot.send_message(
            config.ADMIN_ID, caption, reply_markup=kb.draft_approval_kb(draft_row["id"])
        )


# ---------- Ежедневный пост (бесплатный канал) ----------

async def generate_and_send_draft(bot: Bot) -> None:
    """Вызывается планировщиком утром — готовит пост дня и шлёт админу на одобрение."""
    if not config.ADMIN_ID:
        return

    try:
        draft = content.build_daily_draft()
    except Exception as e:
        await bot.send_message(
            config.ADMIN_ID,
            f"⚠️ Не получилось сгенерировать пост дня: {e}\n\n"
            "Часто причина — Google обновил модель Gemini и старое имя модели "
            "перестало работать. Напиши мне, если увидишь это сообщение — поправлю."
        )
        return

    image_path = None
    if draft["image_bytes"]:
        image_path = f"draft_{dt.date.today().isoformat()}.png"
        with open(image_path, "wb") as f:
            f.write(draft["image_bytes"])

    draft_id = db.create_draft(
        post_date=dt.date.today().isoformat(),
        topic=draft["topic"],
        text=draft["text"],
        image_path=image_path,
        kind="daily",
    )
    draft_row = db.get_draft(draft_id)
    await bot.send_message(config.ADMIN_ID, "🌅 Пост на сегодня готов, гляньте:")
    await send_draft_preview(bot, draft_row)


# ---------- Программа недели (закрытый канал) ----------

async def generate_and_send_weekly_draft(bot: Bot) -> None:
    """Вызывается планировщиком раз в неделю — готовит программу недели на одобрение."""
    if not config.ADMIN_ID:
        return

    try:
        draft = content.build_weekly_draft()
    except Exception as e:
        await bot.send_message(
            config.ADMIN_ID,
            f"⚠️ Не получилось сгенерировать программу недели: {e}"
        )
        return

    monday = _monday_of_current_week().isoformat()
    image_path = None
    if draft["image_bytes"]:
        image_path = f"draft_weekly_{monday}.png"
        with open(image_path, "wb") as f:
            f.write(draft["image_bytes"])

    draft_id = db.create_draft(
        post_date=monday,
        topic=draft["topic"],
        text=draft["text"],
        image_path=image_path,
        kind="weekly",
    )
    draft_row = db.get_draft(draft_id)
    await bot.send_message(config.ADMIN_ID, "🗓️ Программа на новую неделю готова, гляньте:")
    await send_draft_preview(bot, draft_row)


# ---------- Общие хендлеры одобрения/регенерации/правки ----------

@router.callback_query(F.data.startswith("draft_approve:"))
async def approve_draft(callback: CallbackQuery, bot: Bot):
    if not _is_admin(callback.from_user.id):
        return
    draft_id = int(callback.data.split(":")[1])
    db.set_draft_status(draft_id, "approved")
    draft_row = db.get_draft(draft_id)

    now = dt.datetime.now()

    if draft_row["kind"] == "weekly":
        today_is_publish_day = DAY_NAMES[now.weekday()] == config.WEEKLY_PUBLISH_DAY.lower()[:3]
        publish_time_passed = today_is_publish_day and (
            (now.hour, now.minute) >= (config.WEEKLY_PUBLISH_HOUR, config.WEEKLY_PUBLISH_MINUTE)
        )
        if publish_time_passed:
            await callback.message.answer("Одобрено ✅ Публикую программу недели сейчас.")
            from scheduler import publish_weekly_post
            await publish_weekly_post(bot)
        else:
            await callback.message.answer(
                f"Одобрено ✅ Опубликую в закрытом канале в ближайший "
                f"{config.WEEKLY_PUBLISH_DAY} в {config.WEEKLY_PUBLISH_HOUR:02d}:"
                f"{config.WEEKLY_PUBLISH_MINUTE:02d}."
            )
    else:
        publish_time_passed = (now.hour, now.minute) >= (config.PUBLISH_HOUR, config.PUBLISH_MINUTE)
        if publish_time_passed:
            await callback.message.answer(
                f"Одобрено ✅ Время {config.PUBLISH_HOUR:02d}:{config.PUBLISH_MINUTE:02d} уже "
                "прошло сегодня — публикую сейчас."
            )
            from scheduler import publish_daily_post
            await publish_daily_post(bot)
        else:
            await callback.message.answer(
                f"Одобрено ✅ Опубликую автоматически в "
                f"{config.PUBLISH_HOUR:02d}:{config.PUBLISH_MINUTE:02d}."
            )
    await callback.answer()


@router.callback_query(F.data.startswith("draft_regen:"))
async def regenerate_draft(callback: CallbackQuery, bot: Bot):
    if not _is_admin(callback.from_user.id):
        return
    draft_id = int(callback.data.split(":")[1])
    draft_row = db.get_draft(draft_id)
    await callback.answer("Генерирую заново...")
    await callback.message.answer("🔄 Секунду, генерирую новый вариант...")

    try:
        if draft_row["kind"] == "weekly":
            new_draft = content.build_weekly_draft()
        else:
            new_draft = content.build_daily_draft()
    except Exception as e:
        await callback.message.answer(f"⚠️ Не получилось сгенерировать: {e}")
        return

    image_path = None
    if new_draft["image_bytes"]:
        image_path = f"draft_{draft_id}_{dt.datetime.now().timestamp():.0f}.png"
        with open(image_path, "wb") as f:
            f.write(new_draft["image_bytes"])

    db.update_draft(draft_id, new_draft["text"], image_path)
    updated_row = db.get_draft(draft_id)
    await send_draft_preview(bot, updated_row)


@router.callback_query(F.data.startswith("draft_edit:"))
async def edit_draft_start(callback: CallbackQuery, state: FSMContext):
    if not _is_admin(callback.from_user.id):
        return
    draft_id = int(callback.data.split(":")[1])
    await state.set_state(EditDraft.waiting_text)
    await state.update_data(draft_id=draft_id)
    await callback.message.answer("Пришли новый текст поста одним сообщением:")
    await callback.answer()


@router.message(EditDraft.waiting_text)
async def edit_draft_finish(message: Message, state: FSMContext, bot: Bot):
    data = await state.get_data()
    draft_id = data["draft_id"]
    draft_row = db.get_draft(draft_id)
    db.update_draft(draft_id, message.text.strip(), draft_row["image_path"])
    await state.clear()
    updated = db.get_draft(draft_id)
    await message.answer("Текст обновлён:")
    await send_draft_preview(bot, updated)


@router.message(Command("post_today"))
async def cmd_post_today(message: Message, bot: Bot):
    """Ручной запуск подготовки поста дня, если хочется вызвать раньше расписания."""
    if not _is_admin(message.from_user.id):
        return
    await message.answer("Готовлю пост дня...")
    await generate_and_send_draft(bot)


@router.message(Command("post_week"))
async def cmd_post_week(message: Message, bot: Bot):
    """Ручной запуск подготовки программы недели, не дожидаясь расписания."""
    if not _is_admin(message.from_user.id):
        return
    await message.answer("Готовлю программу недели...")
    await generate_and_send_weekly_draft(bot)
