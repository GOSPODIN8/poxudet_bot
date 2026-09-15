from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

import database as db
import keyboards as kb
from states import Survey

router = Router()

GOAL_LABELS = {
    "goal_general": "Похудеть в целом",
    "goal_belly": "Плоский живот",
    "goal_glutes": "Подтянуть ягодицы",
    "goal_other": "Своя цель",
}


@router.message(Survey.name)
async def survey_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text.strip())
    await state.set_state(Survey.age)
    await message.answer("Сколько тебе лет?")


@router.message(Survey.age)
async def survey_age(message: Message, state: FSMContext):
    await state.update_data(age=message.text.strip())
    await state.set_state(Survey.experience)
    await message.answer(
        "Был(а) ли у тебя раньше опыт похудения — диеты, тренировки, попытки?",
        reply_markup=kb.experience_kb(),
    )


@router.callback_query(Survey.experience, F.data.startswith("exp_"))
async def survey_experience(callback: CallbackQuery, state: FSMContext):
    experience = "Да" if callback.data == "exp_yes" else "Нет"
    await state.update_data(experience=experience)
    await state.set_state(Survey.goal)
    await callback.message.edit_text(
        "И последнее — что для тебя сейчас в приоритете?",
        reply_markup=kb.goal_kb(),
    )


@router.callback_query(Survey.goal, F.data.startswith("goal_"))
async def survey_goal(callback: CallbackQuery, state: FSMContext):
    goal_label = GOAL_LABELS.get(callback.data, "Не указано")

    if callback.data == "goal_other":
        await state.update_data(goal_pending=True)
        await callback.message.edit_text("Расскажи своими словами, какая у тебя цель?")
        return

    await finish_survey(callback.message, state, callback.from_user.id, goal_label)
    await callback.answer()


@router.message(Survey.goal)
async def survey_goal_custom(message: Message, state: FSMContext):
    # срабатывает только если человек выбрал "Своя цель" и написал текст
    data = await state.get_data()
    if not data.get("goal_pending"):
        return
    await finish_survey(message, state, message.from_user.id, message.text.strip())


async def finish_survey(message: Message, state: FSMContext, user_id: int, goal_label: str):
    data = await state.get_data()
    db.save_survey(
        user_id=user_id,
        name=data.get("name", ""),
        age=data.get("age", ""),
        experience=data.get("experience", ""),
        goal=goal_label,
    )
    await state.clear()

    name = data.get("name", "")
    await message.answer(
        f"Спасибо, {name}! Теперь у меня есть всё, чтобы предложить то, что подходит именно тебе.\n\n"
        "У меня есть гайд «Похудение без тренировок» — шесть принципов устойчивого "
        "снижения веса и план на первую неделю, без диет и спортзала.",
        reply_markup=kb.buy_guide_kb(),
    )
