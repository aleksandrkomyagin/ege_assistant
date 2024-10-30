from aiogram.fsm.state import State, StatesGroup


class UserRegisterData(StatesGroup):
    telegram_id = State()
    first_name = State()
    last_name = State()


class ScoreData(StatesGroup):
    subject = State()
    score = State()


class Login(StatesGroup):
    login = State()
