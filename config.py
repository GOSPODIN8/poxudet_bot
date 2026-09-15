"""
Все настройки бота берутся из переменных окружения (Environment Variables).
На Railway их нужно будет задать во вкладке "Variables" — см. README.md.
Локально для теста можно создать файл .env (скопируйте .env.example в .env и заполните).
"""
import os
from dotenv import load_dotenv

load_dotenv()  # подхватывает .env файл, если он есть (для локального теста)


def _get_int(name: str, required: bool = True) -> int:
    value = os.getenv(name)
    if not value:
        if required:
            raise RuntimeError(f"Не задана переменная окружения {name}")
        return 0
    return int(value)


# Токен бота, который выдаёт @BotFather
BOT_TOKEN: str = os.getenv("BOT_TOKEN", "")

# ID бесплатного канала, на который нужно подписаться перед анкетой.
# Формат: -100xxxxxxxxxx (узнать ID можно через @userinfobot — переслать ему
# любое сообщение из канала, либо см. README.md)
FREE_CHANNEL_ID: int = _get_int("FREE_CHANNEL_ID", required=False)

# Публичная ссылка/юзернейм бесплатного канала для кнопки "Подписаться"
# Пример: "https://t.me/your_free_channel"
FREE_CHANNEL_URL: str = os.getenv("FREE_CHANNEL_URL", "")

# ID закрытого платного канала — нужен, чтобы бот мог публиковать туда
# посты через /post (бот должен быть админом канала)
CLOSED_CHANNEL_ID: int = _get_int("CLOSED_CHANNEL_ID", required=False)

# Прямая платная ссылка на закрытый канал (invite-ссылка Telegram,
# оплата звёздами идёт напрямую в Telegram при вступлении, мимо бота)
# Пример: "https://t.me/+HdwKZ_AgxZ05MWFi"
CLOSED_CHANNEL_URL: str = os.getenv("CLOSED_CHANNEL_URL", "")

# Ваш Telegram user_id (числом) — куда бот будет слать уведомления
# о новых оплатах и заполненных анкетах. Узнать свой ID можно у @userinfobot
ADMIN_ID: int = _get_int("ADMIN_ID", required=False)

# Цены в Telegram Stars (XTR). 1 звезда = 1 amount, дробных чисел нет.
GUIDE_PRICE_STARS: int = _get_int("GUIDE_PRICE_STARS", required=False) or 250
SUBSCRIPTION_PRICE_STARS: int = _get_int("SUBSCRIPTION_PRICE_STARS", required=False) or 499

# Текст, который бот показывает по кнопке "Где взять Telegram Stars?".
# Впишите сюда любую свою ссылку/инструкцию — этот текст бот отправляет как есть.
STARS_HELP_TEXT: str = os.getenv("STARS_HELP_TEXT") or (
    "Telegram Stars можно купить официально прямо в приложении Telegram:\n\n"
    "Настройки → Telegram Stars → Купить звёзды "
    "(оплата через Apple Pay / Google Pay / карту, в зависимости от устройства).\n\n"
    "Также звёзды можно купить через официальный сервис fragment.com.\n\n"
    "После этого просто вернись сюда и нажми «Купить гайд»."
)

# Путь к файлу гайда, который отправляется после оплаты
GUIDE_FILE_PATH: str = os.getenv("GUIDE_FILE_PATH", "guide.html")


# ---- Автопостинг контента (Gemini) ----

GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")

# Часовой пояс аудитории — используется для расписания публикаций
TIMEZONE: str = os.getenv("TIMEZONE", "Asia/Dushanbe")

# Во сколько бот готовит черновик и присылает вам на одобрение
PREPARE_HOUR: int = _get_int("PREPARE_HOUR", required=False) or 8
PREPARE_MINUTE: int = _get_int("PREPARE_MINUTE", required=False) or 0

# Во сколько бот публикует одобренный черновик в бесплатный канал
PUBLISH_HOUR: int = _get_int("PUBLISH_HOUR", required=False) or 10
PUBLISH_MINUTE: int = _get_int("PUBLISH_MINUTE", required=False) or 0

# Текст-приглашение в закрытый канал, который добавляется под каждым
# ежедневным постом в бесплатном канале
DAILY_CTA_TEXT: str = os.getenv(
    "DAILY_CTA_TEXT",
    "Такие советы — только часть картины. Готовая программа на каждую "
    "неделю и чат поддержки — в закрытом канале 👇",
)
