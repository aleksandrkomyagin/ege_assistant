import logging.config

from dataclasses import dataclass
from environs import Env
from pathlib import Path

from common.datetime_formats import CustomFormatter

BASE_DIR = Path(__file__).resolve().parent.parent


@dataclass
class DatabaseConfig:
    database: str         # Название базы данных
    db_host: str          # URL-адрес базы данных
    db_user: str          # Username пользователя базы данных
    db_password: str      # Пароль к базе данных
    db_port: str      # Пароль к базе данных

    def create_url_db(self):
        url = "%s://%s:%s@%s:%s/%s" % (
            "postgresql+asyncpg", self.db_user, self.db_password,
            self.db_host, int(self.db_port), self.database
        )
        return url


@dataclass
class RedisDatabase:
    url_db: str


@dataclass
class TgBot:
    token: str            # Токен для доступа к телеграм-боту


@dataclass
class Subjects:
    names: list[str]


@dataclass
class Config:
    tg_bot: TgBot
    db: DatabaseConfig
    redis: RedisDatabase
    subjects: Subjects


def load_config(path: Path | None = None) -> Config:

    env: Env = Env()
    env.read_env(path)

    return Config(
        tg_bot=TgBot(
            token=env("BOT_TOKEN")
        ),
        db=DatabaseConfig(
            database=env("POSTGRES_DB"),
            db_host=env("POSTGRES_HOST"),
            db_port=env("POSTGRES_PORT"),
            db_user=env("POSTGRES_USER"),
            db_password=env("POSTGRES_PASSWORD")
        ),
        redis=RedisDatabase(
            url_db=env("REDIS_LOCATION")
        ),
        subjects=Subjects(
            names=env("SUBJECTS")
        )
    )


path_env = BASE_DIR / ".env"

config = load_config(path_env)


LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'mosayc': {
            '()': CustomFormatter,
            'format': '%(asctime)-15s %(levelname)-7s %(message)s',
        }
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'mosayc'
        }
    },
    'loggers': {
        'bot': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

logging.config.dictConfig(LOGGING)
