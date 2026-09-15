from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import config


def subscribe_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Подписаться на канал", url=config.FREE_CHANNEL_URL)],
        [InlineKeyboardButton(text="✅ Я подписался(-ась)", callback_data="check_sub")],
    ])


def experience_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, пробовала", callback_data="exp_yes")],
        [InlineKeyboardButton(text="Нет, это будет впервые", callback_data="exp_no")],
    ])


def goal_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Похудеть в целом", callback_data="goal_general")],
        [InlineKeyboardButton(text="Плоский живот", callback_data="goal_belly")],
        [InlineKeyboardButton(text="Подтянуть ягодицы", callback_data="goal_glutes")],
        [InlineKeyboardButton(text="Своя цель", callback_data="goal_other")],
    ])


def buy_guide_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"💫 Купить гайд за {config.GUIDE_PRICE_STARS} ⭐",
            callback_data="buy_guide",
        )],
        [InlineKeyboardButton(text="Где взять Telegram Stars?", callback_data="stars_help")],
    ])


def join_closed_channel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"💫 Присоединиться за {config.SUBSCRIPTION_PRICE_STARS} ⭐/мес",
            url=config.CLOSED_CHANNEL_URL,
        )],
    ])
