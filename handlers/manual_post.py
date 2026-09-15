import os
import time

from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

import config
import gemini_client
import keyboards as kb
from states import ManualPost

router = Router()


def _is_admin(user_id: int) -> bool:
    return config.ADMIN_ID and user_id == config.ADMIN_ID


@router.message(Command("post"))
async def cmd_post(message: Message, state: FSMContext):
    if not _is_admin(message.from_user.id):
        return
    await state.clear()
    await state.set_state(ManualPost.channel)
    await message.answer("В какой канал публикуем?", reply_markup=kb.channel_choice_kb())


@router.callback_query(ManualPost.channel, F.data.startswith("post_channel:"))
async def manual_channel_chosen(callback: CallbackQuery, state: FSMContext):
    channel = callback.data.split(":")[1]  # "free" или "closed"
    await state.update_data(channel=channel)
    await state.set_state(ManualPost.text)
    await callback.message.edit_text("Пришли текст поста одним сообщением:")
    await callback.answer()


@router.message(ManualPost.text)
async def manual_text_received(message: Message, state: FSMContext):
    await state.update_data(text=message.text.strip())
    await state.set_state(ManualPost.want_image)
    await message.answer("Добавить картинку (сгенерирую через Gemini)?", reply_markup=kb.yes_no_kb("want_img"))


@router.callback_query(ManualPost.want_image, F.data.startswith("want_img:"))
async def manual_want_image(callback: CallbackQuery, state: FSMContext):
    answer = callback.data.split(":")[1]
    if answer == "yes":
        await state.set_state(ManualPost.image_prompt)
        await callback.message.edit_text("Опиши, что должно быть на картинке (пара слов достаточно):")
    else:
        await state.update_data(image_path=None)
        await state.set_state(ManualPost.button_text)
        await callback.message.edit_text("Текст на кнопке (например «Подробнее»):")
    await callback.answer()


@router.message(ManualPost.image_prompt)
async def manual_image_prompt(message: Message, state: FSMContext):
    await message.answer("🎨 Генерирую картинку...")
    image_bytes = gemini_client.generate_image(message.text.strip())
    image_path = None
    if image_bytes:
        image_path = f"manual_post_{int(time.time())}.png"
        with open(image_path, "wb") as f:
            f.write(image_bytes)
        await message.answer_photo(FSInputFile(image_path), caption="Вот такая картинка получилась")
    else:
        await message.answer("Не получилось сгенерировать картинку, продолжаем без неё.")

    await state.update_data(image_path=image_path)
    await state.set_state(ManualPost.button_text)
    await message.answer("Текст на кнопке (например «Подробнее»):")


@router.message(ManualPost.button_text)
async def manual_button_text(message: Message, state: FSMContext):
    await state.update_data(button_text=message.text.strip())
    await state.set_state(ManualPost.button_url)
    await message.answer("Ссылка, куда ведёт кнопка (полный адрес, начинается с https://):")


@router.message(ManualPost.button_url)
async def manual_button_url(message: Message, state: FSMContext, bot: Bot):
    await state.update_data(button_url=message.text.strip())
    data = await state.get_data()
    await state.set_state(ManualPost.confirm)

    preview_text = f"{data['text']}\n\n— предпросмотр —\nКнопка: «{data['button_text']}» → {data['button_url']}"
    if data.get("image_path") and os.path.exists(data["image_path"]):
        await message.answer_photo(FSInputFile(data["image_path"]), caption=preview_text[:1024])
    else:
        await message.answer(preview_text)

    channel_label = "бесплатный канал" if data["channel"] == "free" else "закрытый канал"
    await message.answer(f"Опубликовать в {channel_label}?", reply_markup=kb.manual_post_confirm_kb())


@router.callback_query(ManualPost.confirm, F.data == "manual_publish")
async def manual_publish(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    chat_id = config.FREE_CHANNEL_ID if data["channel"] == "free" else config.CLOSED_CHANNEL_ID

    if not chat_id:
        await callback.message.answer(
            "Не настроен ID этого канала в переменных окружения (FREE_CHANNEL_ID / "
            "CLOSED_CHANNEL_ID) — публикация невозможна."
        )
        await state.clear()
        await callback.answer()
        return

    from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
    post_kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=data["button_text"], url=data["button_url"])]
    ])

    try:
        if data.get("image_path") and os.path.exists(data["image_path"]):
            await bot.send_photo(
                chat_id, FSInputFile(data["image_path"]),
                caption=data["text"][:1024], reply_markup=post_kb,
            )
        else:
            await bot.send_message(chat_id, data["text"], reply_markup=post_kb)
        await callback.message.answer("Опубликовано ✅")
    except Exception as e:
        await callback.message.answer(
            f"Не получилось опубликовать: {e}\n\n"
            "Проверь, что бот — администратор в этом канале."
        )

    await state.clear()
    await callback.answer()


@router.callback_query(ManualPost.confirm, F.data == "manual_cancel")
async def manual_cancel(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.answer("Отменено.")
    await callback.answer()
