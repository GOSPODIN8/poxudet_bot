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

# ID закрытого платного канала (нужен, только если захотите позже
# автоматизировать проверку доступа — сейчас не используется)
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

# Путь к файлу гайда, который отправляется после оплаты
GUIDE_FILE_PATH: str = os.getenv("GUIDE_FILE_PATH", "guide.html")
