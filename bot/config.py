import os
from typing import List

from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.client.default import DefaultBotProperties
from loguru import logger
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    BOT_TOKEN: str
    ADMIN_IDS: List[int]
    PROVIDER_TOKEN: str
    FORMAT_LOG: str = '{time:YYYY-MM-DD at HH:mm:ss} | {level} | {message}'
    LOG_ROTATION: str = '10 MB'
    DATABASE_PORT: int
    POSTGRES_PASSWORD: str
    POSTGRES_USER: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    model_config = SettingsConfigDict(
        env_file=os.path.join(
            os.path.dirname(os.path.abspath(__file__)), '..', '.env'
            )
    )


settings = Settings()


def get_db_url():
    return (f'postgresql+asyncpg://{settings.POSTGRES_USER}:'
            f'{settings.POSTGRES_PASSWORD}@'
            f'{settings.POSTGRES_HOST}:{settings.DATABASE_PORT}/'
            f'{settings.POSTGRES_DB}'
            )


bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
    )
dp = Dispatcher(storage=MemoryStorage())
admins = settings.ADMIN_IDS

log_file_path = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), 'log.txt'
    )
logger.add(
    log_file_path,
    format=settings.FORMAT_LOG,
    level='INFO',
    rotation=settings.LOG_ROTATION
    )
database_url = get_db_url()
