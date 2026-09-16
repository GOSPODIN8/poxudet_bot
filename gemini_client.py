"""
Обёртка над Gemini API: генерация текста поста и картинки к нему.

Модель для текста — gemini-3.6-flash (актуальная стабильная flash-модель
Google на 2026 год; более ранняя gemini-2.5-flash уже снята с поддержки
для новых проектов).
Модель для картинок — gemini-3.1-flash-image ("Nano Banana").

Google периодически меняет актуальные модели и отключает старые — если
через несколько месяцев снова появится ошибка вида "model ... is no longer
available", просто замените имя модели здесь на то, что укажет Google в
тексте ошибки.
"""
from google import genai
from google.genai import types

import config

_client: genai.Client | None = None


def _get_client() -> genai.Client:
    global _client
    if _client is None:
        _client = genai.Client(api_key=config.GEMINI_API_KEY)
    return _client


def generate_tip_text(topic_prompt: str) -> str:
    """Генерирует текст короткого поста-совета по заданной теме (для ежедневных постов)."""
    system_prompt = (
        "Ты ведёшь Telegram-канал про похудение без тренировок и жёстких диет. "
        "Тон — тёплый, поддерживающий, без осуждения и без давления. "
        "Никаких конкретных цифр калорий, норм веса или сроков похудения — "
        "только принципы и практичные советы. "
        "Пиши по-русски, для Telegram-поста, не длиннее 700 символов, "
        "без хэштегов и без markdown-разметки. "
        "Не добавляй в конце призыв подписаться на что-либо — это добавится отдельно."
    )
    return generate_tip_text_raw(f"{system_prompt}\n\nТема сегодняшнего поста: {topic_prompt}")


def generate_tip_text_raw(full_prompt: str) -> str:
    """То же самое, но с полностью готовым промптом — для других сценариев (например, недельная программа)."""
    client = _get_client()
    response = client.models.generate_content(
        model="gemini-3.6-flash",
        contents=full_prompt,
    )
    return (response.text or "").strip()


def generate_image(image_prompt: str) -> bytes | None:
    """Генерирует картинку и возвращает её байты (PNG) или None при неудаче."""
    client = _get_client()
    full_prompt = (
        f"{image_prompt}. Стиль: мягкая плоская иллюстрация, спокойная приглушённая "
        "палитра (шалфейно-зелёный, тёплый бежевый, немного терракотового), "
        "минимализм, без текста и надписей на картинке, без логотипов, "
        "без фотореалистичных лиц конкретных людей."
    )
    response = client.models.generate_content(
        model="gemini-3.1-flash-image",
        contents=full_prompt,
        config=types.GenerateContentConfig(
            response_modalities=["TEXT", "IMAGE"],
        ),
    )
    for part in response.candidates[0].content.parts:
        if part.inline_data:
            return part.inline_data.data
    return None
