import asyncio

from aiogram.types import BotCommand, BotCommandScopeDefault
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from loguru import logger

from bot.config import bot, admins, dp
from bot.dao.database_middleware import (
    DatabaseMiddlewareWithoutCommit,
    DatabaseMiddlewareWithCommit
)
from bot.admin.admin import admin_router
from bot.user.catalog_router import catalog_router
from bot.user.service_router import service_router
from bot.user.user_router import user_router
from bot.utils.constants import SCHEDULER_HOUR, SCHEDULER_MINUTE
from bot.utils.excel_to_json import excel_to_json
from bot.utils.outlook_parse import parse_price_data
from bot.utils.parts_update_data import update_parts_data


scheduler = AsyncIOScheduler()


scheduler.add_job(
    parse_price_data,
    'cron',
    day_of_week='mon-sun',
    hour=SCHEDULER_HOUR,
    minute=SCHEDULER_MINUTE,
    id='parse_price_data',
    replace_existing=True
    )
scheduler.add_job(
    excel_to_json,
    'cron',
    day_of_week='mon-sun',
    hour=SCHEDULER_HOUR,
    minute=SCHEDULER_MINUTE+1,
    id='excel_to_json',
    replace_existing=True
    )
scheduler.add_job(
    update_parts_data,
    'cron',
    day_of_week='mon-sun',
    hour=SCHEDULER_HOUR,
    minute=SCHEDULER_MINUTE+2,
    id='update_parts_data',
    replace_existing=True
    )


# Функция, которая настроит командное меню (дефолтное для всех пользователей)
async def set_commands():
    commands = [BotCommand(command='start', description='Старт')]
    await bot.set_my_commands(commands, BotCommandScopeDefault())


# Функция, которая выполнится, когда бот запустится
async def start_bot():
    await set_commands()
    for admin_id in admins:
        try:
            await bot.send_message(admin_id, 'Бот запущен.')
        except Exception as error:
            logger.error(
                f'Ошибка при запуске бота: {error}'
                )
    logger.info('Бот успешно запущен.')


# Функция, которая выполнится, когда бот завершит свою работу
async def stop_bot():
    try:
        for admin_id in admins:
            await bot.send_message(admin_id, 'Бот остановлен.')
    except Exception as error:
        logger.error(
            f'Ошибка при остановке бота: {error}'
            )
    logger.error('Бот остановлен!')


async def main():
    scheduler.start()
    # Регистрация мидлварей
    dp.update.middleware.register(DatabaseMiddlewareWithoutCommit())
    dp.update.middleware.register(DatabaseMiddlewareWithCommit())

    # Регистрация роутеров
    dp.include_router(catalog_router)
    dp.include_router(user_router)
    dp.include_router(admin_router)
    dp.include_router(service_router)

    # Регистрация функций
    dp.startup.register(start_bot)
    dp.shutdown.register(stop_bot)

    # Запуск бота в режиме long polling
    try:
        await bot.delete_webhook(drop_pending_updates=True)
        await dp.start_polling(
            bot,
            allowed_updates=dp.resolve_used_update_types()
            )
    finally:
        await bot.session.close()

if __name__ == '__main__':
    asyncio.run(main())
