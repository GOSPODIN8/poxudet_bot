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


def daily_post_cta_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔒 Закрытый канал", url=config.CLOSED_CHANNEL_URL)],
    ])


def draft_approval_kb(draft_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Одобрить", callback_data=f"draft_approve:{draft_id}")],
        [InlineKeyboardButton(text="🔄 Сгенерировать заново", callback_data=f"draft_regen:{draft_id}")],
        [InlineKeyboardButton(text="✏️ Изменить текст", callback_data=f"draft_edit:{draft_id}")],
    ])


def channel_choice_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="📢 Бесплатный канал", callback_data="post_channel:free")],
        [InlineKeyboardButton(text="🔒 Закрытый канал", callback_data="post_channel:closed")],
    ])


def yes_no_kb(prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да", callback_data=f"{prefix}:yes")],
        [InlineKeyboardButton(text="Нет", callback_data=f"{prefix}:no")],
    ])


def manual_post_confirm_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Опубликовать", callback_data="manual_publish")],
        [InlineKeyboardButton(text="❌ Отмена", callback_data="manual_cancel")],
    ])


def join_closed_channel_kb() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=f"💫 Присоединиться за {config.SUBSCRIPTION_PRICE_STARS} ⭐/мес",
            url=config.CLOSED_CHANNEL_URL,
        )],
    ])
