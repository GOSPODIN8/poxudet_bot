from aiogram.fsm.state import State, StatesGroup


class Survey(StatesGroup):
    """Шаги анкеты, которая открывается после подписки на бесплатный канал."""
    name = State()
    age = State()
    experience = State()
    goal = State()
