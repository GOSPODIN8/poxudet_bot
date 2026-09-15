"""
Этот роутер должен быть подключён ПОСЛЕДНИМ в bot.py — он ловит все
апдейты, которые не подошли ни под один из предыдущих хендлеров.
Раньше такие апдейты просто пропадали (в логах Railway это было видно как
"is not handled"). Теперь бот вежливо ответит и запишет в лог, что именно
пришло — это поможет понять причину, если такое повторится.
"""
import logging

from aiogram import Router
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

router = Router()


@router.callback_query()
async def fallback_callback(callback: CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    logging.warning(
        "Необработанный callback: data=%r, user_id=%s, state=%s",
        callback.data, callback.from_user.id, current_state,
    )
    await callback.answer(
        "Эта кнопка уже неактуальна — попробуйте начать действие заново.",
        show_alert=True,
    )


@router.message()
async def fallback_message(message: Message, state: FSMContext):
    current_state = await state.get_state()
    logging.warning(
        "Необработанное сообщение: text=%r, user_id=%s, state=%s",
        message.text, message.from_user.id, current_state,
    )
    if current_state is None:
        await message.answer(
            "Не совсем понял(а). Напиши /start, чтобы начать заново."
        )
