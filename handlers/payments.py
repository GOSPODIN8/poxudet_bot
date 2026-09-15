from aiogram import Router, F, Bot
from aiogram.types import (
    Message, CallbackQuery, PreCheckoutQuery, LabeledPrice, FSInputFile,
)

import config
import database as db
import keyboards as kb

router = Router()

GUIDE_PAYLOAD = "guide_purchase"


# ---------- Покупка гайда ----------

@router.callback_query(F.data == "buy_guide")
async def buy_guide(callback: CallbackQuery, bot: Bot):
    await bot.send_invoice(
        chat_id=callback.from_user.id,
        title="Гайд «Похудение без тренировок»",
        description="6 принципов устойчивого похудения без диет и спортзала + план на первую неделю.",
        payload=GUIDE_PAYLOAD,
        currency="XTR",  # Telegram Stars
        prices=[LabeledPrice(label="Гайд", amount=config.GUIDE_PRICE_STARS)],
    )
    await callback.answer()


@router.callback_query(F.data == "stars_help")
async def stars_help(callback: CallbackQuery):
    await callback.message.answer(config.STARS_HELP_TEXT)
    await callback.answer()


# ---------- Обязательные хендлеры для приёма оплаты ----------

@router.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery, bot: Bot):
    # Telegram требует подтвердить оплату в течение 10 секунд
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment(message: Message, bot: Bot):
    payload = message.successful_payment.invoice_payload

    if payload == GUIDE_PAYLOAD:
        await deliver_guide(message, bot)

    if config.ADMIN_ID:
        await bot.send_message(
            config.ADMIN_ID,
            f"💰 Новая оплата!\n"
            f"Пользователь: @{message.from_user.username or message.from_user.id}\n"
            f"Товар: {payload}\n"
            f"Сумма: {message.successful_payment.total_amount} ⭐",
        )


async def deliver_guide(message: Message, bot: Bot):
    db.mark_guide_bought(message.from_user.id)
    await message.answer("Оплата прошла ✅ Вот твой гайд:")
    await message.answer_document(FSInputFile(config.GUIDE_FILE_PATH))

    await message.answer(
        "Это база. Дальше — самое сложное: удерживать это не пару дней, а несколько "
        "недель подряд, когда рядом никто не подталкивает и легко забросить.\n\n"
        "В закрытом канале — готовая программа на каждую неделю (не нужно придумывать "
        "самой, что делать сегодня) и чат, где девочки поддерживают друг друга и "
        "делятся результатами.",
        reply_markup=kb.join_closed_channel_kb(),
    )




