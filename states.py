from aiogram.fsm.state import State, StatesGroup


class Survey(StatesGroup):
    """Шаги анкеты, которая открывается после подписки на бесплатный канал."""
    name = State()
    age = State()
    experience = State()
    goal = State()


class ManualPost(StatesGroup):
    """Ручная публикация поста через команду /post."""
    channel = State()
    text = State()
    want_image = State()
    image_prompt = State()
    button_text = State()
    button_url = State()
    confirm = State()


class EditDraft(StatesGroup):
    """Правка текста автосгенерированного ежедневного черновика."""
    waiting_text = State()
