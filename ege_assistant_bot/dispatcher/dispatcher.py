from datetime import timedelta

from aiogram import Dispatcher, F
from aiogram.filters import CommandStart, StateFilter
from aiogram.fsm.state import default_state
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from config.config import Config
from config.config import config as c
from database.db import create_pool
from handlers import handlers
from middlewares.middlewares import DBSessionMiddleware
from state.states import UserRegisterData, ScoreData


subjects = c.subjects.names.split(",")


async def _get_storage(config: Config):
    default_ttl = timedelta(days=1)
    redis = Redis.from_url(config.redis.url_db)
    storage = RedisStorage(
        redis=redis,
        state_ttl=default_ttl,
        data_ttl=default_ttl
    )
    return storage


def _setup_outer_middlewares(dispatcher: Dispatcher, config: Config) -> None:
    pool = dispatcher["session_pool"] = create_pool(config.db.create_url_db())

    dispatcher.update.outer_middleware(DBSessionMiddleware(session_pool=pool))


def _register_handlers(dispatcher: Dispatcher):
    dispatcher.message.register(
        handlers.process_start_command,
        CommandStart(),
        StateFilter(default_state)
    )
    dispatcher.message.register(
        handlers.process_login,
        F.text == "/login"
    )
    dispatcher.message.register(
        handlers.process_register,
        StateFilter(default_state),
        F.text == "/register"
    )
    dispatcher.message.register(
        handlers.process_cancel_register,
        ~StateFilter(default_state),
        F.text == "/cancel_register"
    )
    dispatcher.message.register(
        handlers.process_cancel,
        ~StateFilter(default_state),
        F.text == "/cancel"
    )
    dispatcher.message.register(
        handlers.process_first_name_sent,
        StateFilter(UserRegisterData.first_name),
        F.text.isalpha()
    )
    dispatcher.message.register(
        handlers.warning_not_first_name,
        StateFilter(UserRegisterData.first_name)
    )
    dispatcher.message.register(
        handlers.process_last_name_sent,
        StateFilter(UserRegisterData.last_name),
        F.text.isalpha()
    )
    dispatcher.message.register(
        handlers.warning_not_last_name,
        StateFilter(UserRegisterData.last_name)
    )
    dispatcher.message.register(
        handlers.process_enter_scores,
        F.text == "/enter_scores"
    )
    dispatcher.message.register(
        handlers.process_subject_sent,
        StateFilter(ScoreData.subject),
        F.text.in_(subjects)
    )
    dispatcher.message.register(
        handlers.warning_not_subject,
        StateFilter(ScoreData.subject)
    )
    dispatcher.message.register(
        handlers.process_score_sent,
        StateFilter(ScoreData.score),
        lambda x: x.text.isdigit() and 0 < int(x.text) < 100
    )
    dispatcher.message.register(
        handlers.warning_not_score,
        StateFilter(ScoreData.score)
    )
    dispatcher.message.register(
        handlers.process_view_scores,
        F.text == "/view_scores"
    )


async def create_dispatcher(config: Config) -> Dispatcher:
    dispatcher: Dispatcher = Dispatcher(storage=await _get_storage(config))
    _register_handlers(dispatcher=dispatcher)
    _setup_outer_middlewares(dispatcher=dispatcher, config=config)
    return dispatcher
