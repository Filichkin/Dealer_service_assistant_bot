from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.types import (
    Message,
    CallbackQuery,
    LabeledPrice,
    PreCheckoutQuery
)
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import bot, settings
from bot.dao.dao import UserDAO, ServiceDao, PaymentDao
from bot.user.kbs import (
    main_user_kb,
    catalog_kb,
    service_kb,
    get_service_buy_kb
)
from bot.user.schemas import TelegramIDModel, PaymentData


catalog_router = Router()


@catalog_router.callback_query(F.data == 'catalog')
async def page_catalog(
    call: CallbackQuery,
    session_without_commit: AsyncSession
):
    await call.answer('Загрузка каталога...')
    catalog_data = await ServiceDao.find_all(session=session_without_commit)

    await call.message.edit_text(
        text='Выберите сервис:',
        reply_markup=catalog_kb(catalog_data)
    )


@catalog_router.callback_query(F.data.startswith('service_'))
async def page_service(
    call: CallbackQuery,
    session_without_commit: AsyncSession
):
    service_id = int(call.data.split('_')[-1])
    service = await ServiceDao.find_one_or_none_by_id(
        session=session_without_commit,
        data_id=service_id
    )
    if service:
        service_text = (
            f'📦 <b>Название товара:</b> {service.name}\n\n'
            f'💰 <b>Цена:</b> {service.price} руб.\n\n'
            f'📝 <b>Описание:</b>\n<i>{service.description}</i>\n\n'
            f'━━━━━━━━━━━━━━━━━━'
        )
        await call.message.answer(
            service_text,
            reply_markup=service_kb(service.id, service.price)
        )
    else:
        await call.answer('О данном сервисе нет информации.')
