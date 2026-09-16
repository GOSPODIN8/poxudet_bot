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


async def send_draft_preview(bot: Bot, draft_row) -> None:
    caption = f"Черновик поста на {draft_row['post_date']}\n\n{draft_row['text']}"
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
    )
    draft_row = db.get_draft(draft_id)
    await bot.send_message(config.ADMIN_ID, "🌅 Пост на сегодня готов, гляньте:")
    await send_draft_preview(bot, draft_row)


@router.callback_query(F.data.startswith("draft_approve:"))
async def approve_draft(callback: CallbackQuery, bot: Bot):
    if not _is_admin(callback.from_user.id):
        return
    draft_id = int(callback.data.split(":")[1])
    db.set_draft_status(draft_id, "approved")

    now = dt.datetime.now()
    publish_time_passed = (now.hour, now.minute) >= (config.PUBLISH_HOUR, config.PUBLISH_MINUTE)

    if publish_time_passed:
        await callback.message.answer(
            f"Одобрено ✅ Время {config.PUBLISH_HOUR:02d}:{config.PUBLISH_MINUTE:02d} уже "
            "прошло сегодня — публикую сейчас."
        )
        from scheduler import publish_daily_post  # локальный импорт, чтобы избежать цикла
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
    await callback.answer("Генерирую заново...")
    await callback.message.answer("🔄 Секунду, генерирую новый вариант...")

    try:
        draft = content.build_daily_draft()
    except Exception as e:
        await callback.message.answer(f"⚠️ Не получилось сгенерировать: {e}")
        return

    image_path = None
    if draft["image_bytes"]:
        image_path = f"draft_{draft_id}_{dt.datetime.now().timestamp():.0f}.png"
        with open(image_path, "wb") as f:
            f.write(draft["image_bytes"])

    db.update_draft(draft_id, draft["text"], image_path)
    draft_row = db.get_draft(draft_id)
    await send_draft_preview(bot, draft_row)


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
