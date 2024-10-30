import logging

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from state.states import UserRegisterData, ScoreData
from database.models import Student, StudentScore, Subject


router = Router()
logger = logging.getLogger("bot")
logger.setLevel(logging.DEBUG)


def create_subjects_keyboard(subjects):
    return [[KeyboardButton(text=f"{subject.name}")] for subject in subjects]


async def get_subjects(session: AsyncSession):
    stmt = select(Subject)
    result = await session.scalars(stmt)
    return result.all()


async def get_user_by_telegram_id(telegram_id: int, session: AsyncSession):
    stmt = select(Student).where(Student.telegram_id == telegram_id)
    result = await session.scalar(stmt)
    return result


async def get_subject_by_name(name: str, session: AsyncSession):
    stmt = select(Subject).where(Subject.name == name)
    result = await session.scalar(stmt)
    return result


async def check_number_in_db_command(telegram_id: int, session: AsyncSession):
    stmt = select(Student).where(Student.telegram_id == telegram_id)
    res = await session.execute(stmt)
    return res.one_or_none()


async def process_start_command(message: Message, state: FSMContext):
    logger.info("Пользователь %s начал взаимодействие с ботом" % message.chat.id)
    await state.clear()
    await message.answer(
        text="Привет!\nЧтобы пользоваться ботом нужно войти в аккаунт /login "
             "или зарегистрироваться /register",

    )


async def process_login(
        message: Message,
        state: FSMContext,
        session: AsyncSession
):
    logger.info("Пользователь %s дал доступ к своему профилю" % message.chat.id)
    user = await check_number_in_db_command(
        telegram_id=message.chat.id,
        session=session
    )

    if not user:
        logger.info("Пользователь %s не найден в БД" % message.chat.id)
        await state.update_data(
            telegram_id=message.chat.id
        )
        await message.answer(
            text="Твои данные не найдены. Нужно зарегистрироваться /register"
        )
        return

    await state.update_data(login=True)
    await message.answer(
        text="Успешная авторизация"
    )
    logger.info(
        "Пользователь %s успешно авторизовался" % message.chat.id
    )


async def process_register(message: Message, state: FSMContext):
    logger.info(
        "Пользователь %s начал регистрацию" % message.chat.id
    )
    await message.answer(text="Введи свое имя")
    await state.set_state(UserRegisterData.first_name)


async def process_cancel_register(message: Message, state: FSMContext):
    logger.info(
        "Пользователь %s отменил регистрации" % message.chat.id
    )
    await message.answer(
        text="Ты отменил регистрацию\n\n"
             "Чтобы снова перейти к заполнению анкеты - "
             "нажми кнопку /register"
    )
    await state.clear()


async def process_cancel(message: Message, state: FSMContext):
    await message.answer(
        text="Действие отменено"
    )
    await state.clear()
    await state.update_data(login=True)


async def process_first_name_sent(message: Message, state: FSMContext):
    logger.info(
        "Пользователь %s ввел имя %s для регистрации" % (message.chat.id, message.text)
    )
    await state.update_data(first_name=message.text)
    await message.answer(text="Спасибо!\n\nА теперь введи свою фамилию")
    await state.set_state(UserRegisterData.last_name)


async def warning_not_first_name(message: Message):
    logger.info(
        "Пользователь %s ввел некорректное имя %s при регистрации" % (message.chat.id, message.text)
    )
    await message.answer(
        text="То, что ты отправил не похоже на имя\n\n"
             "Пожалуйста, введи свое имя\n\n"
             "Если ты хочешь прервать заполнение анкеты - "
             "нажми кнопку /cancel_register"
    )


async def process_last_name_sent(message: Message, state: FSMContext, session: AsyncSession):
    logger.info(
        "Пользователь %s ввел фамилию %s для регистрации" % (message.chat.id, message.text)
    )
    await state.update_data(last_name=message.text)
    data = await state.get_data()
    first_name = data.get("first_name")
    last_name = data.get("last_name")
    instance = Student(
        first_name=first_name,
        last_name=last_name,
        telegram_id=message.chat.id
    )
    session.add(instance)
    await session.commit()
    await state.clear()
    await state.update_data(login=True)
    await message.answer(
        text="Спасибо!\n\n"
             "Регистрация пройдена.\n\n"
             "Можешь сохранить или посмотреть сохраненные баллы"
    )
    logger.info(
        "Пользователь %s успешно зарегистрировался" % message.chat.id
    )


async def warning_not_last_name(message: Message):
    logger.info(
        "Пользователь %s ввел некорректною фамилию %s для регистрации" % (message.chat.id, message.text)
    )
    await message.answer(
        text="То, что ты отправил не похоже на фамилию\n\n"
             "Пожалуйста, введи свою фамилию\n\n"
             "Если ты хочешь прервать заполнение анкеты - "
             "нажми кнопку /cancel"
    )


async def process_enter_scores(message: Message, state: FSMContext, session: AsyncSession):
    login = await state.get_data()
    if not login.get("login"):
        await message.answer(
            text="Чтобы сохранить результат экзамена, нужно войти в аккаунт /login"
        )
        logger.info(
            "Пользователь %s пытался сохранить баллы без авторизации" % message.chat.id
        )
        return
    logger.info(
        "Пользователь %s начал процесс сохранения баллов" % message.chat.id
    )
    subjects = await get_subjects(session)
    keyboard = create_subjects_keyboard(subjects)
    await state.set_state(ScoreData.subject)
    await message.answer(
        text="Выбери предмет, для которого нужно сохранить баллы\n"
             "Если ты хочешь прервать сохранение баллов - "
             "нажми кнопку /cancel",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=keyboard,
            resize_keyboard=True,
            one_time_keyboard=True
        )
    )


async def process_subject_sent(message: Message, state: FSMContext):
    logger.info(
        "Пользователь %s выбрал предмет %s для сохранения баллов" % (message.chat.id, message.text)
    )
    await state.update_data(subject=message.text)
    await message.answer(
        text="Теперь введите сумму баллов\n"
             "Если ты хочешь прервать сохранение баллов - "
             "нажми кнопку /cancel"
    )
    await state.set_state(ScoreData.score)


async def warning_not_subject(message: Message):
    logger.info(
        "Пользователь %s ввел некорректный предмет %s" % (message.chat.id, message.text)
    )
    await message.answer(text="Доступны только предметы из списка")


async def process_score_sent(message: Message, state: FSMContext, session: AsyncSession):
    logger.info(
        "Пользователь %s ввел количество баллов %s" % (message.chat.id, message.text)
    )
    await state.update_data(score=message.text)
    data = await state.get_data()
    subject = data.get("subject")
    score = int(data.get("score"))
    student = await get_user_by_telegram_id(message.chat.id, session)
    subject = await get_subject_by_name(subject, session)
    instance = StudentScore(
        student_id=student.id,
        subject_id=subject.id,
        score=score
    )
    session.add(instance)
    await session.commit()
    logger.info(
        "Пользователь %s успешно сохранил баллы" % message.chat.id
    )
    await message.answer(text="Баллы сохранены")
    await state.clear()
    await state.update_data(login=True)


async def warning_not_score(message: Message):
    logger.info(
        "Пользователь %s ввел некорректную сумму баллов %s" % (message.chat.id, message.text)
    )
    await message.answer(text="Введи корректные данные")


async def process_view_scores(message: Message, state: FSMContext, session: AsyncSession):
    login = await state.get_data()
    if not login.get("login"):
        await message.answer(
            text="Чтобы посмотреть сохраненные результаты, нужно войти в аккаунт /login"
        )
        logger.info(
            "Пользователь %s пытался посмотреть сохраненные баллы без авторизации" % message.chat.id
        )
        return
    stmt = select(StudentScore).join(Student, Student.telegram_id == message.chat.id)
    result = await session.scalars(stmt)
    result = [f"{res.subject.name}: {res.score}" for res in result]
    if not result:
        await message.answer(text="Пока ничего не сохранено")
        return
    await message.answer(text="\n".join(result))
