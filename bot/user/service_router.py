from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
)
from sqlalchemy.ext.asyncio import AsyncSession

from bot.dao.dao import ServiceDao
from bot.user.kbs import home_kb


service_router = Router()


@service_router.callback_query(F.data.startswith('user_service_'))
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
            f'📦 <b>Название сервиса:</b> {service.name}\n\n'
            f'💰 <b>Цена:</b> {service.price} руб.\n\n'
            f'📝 <b>Описание:</b>\n<i>{service.description}</i>\n\n'
            f'━━━━━━━━━━━━━━━━━━'
        )
        await call.message.answer(
            service_text,
            reply_markup=home_kb()
        )
    else:
        await call.answer('О данном сервисе нет информации.')
