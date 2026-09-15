from aiogram import Router, F, Bot
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import config
import database as db
import keyboards as kb
from states import Survey

router = Router()


async def is_subscribed(bot: Bot, user_id: int) -> bool:
    if not config.FREE_CHANNEL_ID:
        # Если канал не настроен — не блокируем анкету (удобно для теста)
        return True
    try:
        member = await bot.get_chat_member(config.FREE_CHANNEL_ID, user_id)
        return member.status in ("member", "administrator", "creator")
    except Exception:
        return False


WELCOME_TEXT = (
    "Привет! 👋\n\n"
    "Здесь — простые и адекватные способы похудеть без изнуряющих тренировок "
    "и жёстких диет.\n\n"
    "Чтобы получить доступ к бесплатным советам и персональным рекомендациям, "
    "сначала подпишись на канал 👇"
)


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, bot: Bot):
    await state.clear()
    db.upsert_user(message.from_user.id, message.from_user.username)

    if await is_subscribed(bot, message.from_user.id):
        await start_survey(message, state)
    else:
        await message.answer(WELCOME_TEXT, reply_markup=kb.subscribe_kb())


@router.callback_query(F.data == "check_sub")
async def check_subscription(callback: CallbackQuery, state: FSMContext, bot: Bot):
    if await is_subscribed(bot, callback.from_user.id):
        await callback.message.delete()
        await start_survey(callback.message, state)
    else:
        await callback.answer(
            "Пока не вижу подписку 🙈 Подпишись и нажми кнопку ещё раз.",
            show_alert=True,
        )


async def start_survey(message: Message, state: FSMContext):
    await state.set_state(Survey.name)
    await message.answer(
        "Отлично, ты подписалась! 🎉\n\n"
        "Задам пару вопросов, чтобы предложить то, что подходит именно тебе.\n\n"
        "Как тебя зовут?"
    )
