from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message
)
from sqlalchemy.ext.asyncio import AsyncSession

from bot.dao.dao import ServiceDao
from bot.user.kbs import cancel_kb_inline, user_kb_back


service_router = Router()


@service_router.callback_query(
        F.data.startswith('user_service_')
    )
async def page_service(
    call: CallbackQuery,
    session_without_commit: AsyncSession,
):
    service_id = int(call.data.split('_')[-1])
    service = await ServiceDao.find_one_or_none_by_id(
        session=session_without_commit,
        data_id=service_id
    )
    if 'VIN' in str(service.name):
        await call.answer('Запущен VIN decoder.')
        service_text = (
            'Введите локальный VIN'
        )
        await call.message.answer(
            service_text,
            reply_markup=cancel_kb_inline()
        )
    else:
        await call.answer('О данном сервисе нет информации.')


@service_router.message(
        F.text
    )
async def vin_decoder(message: Message):
    vin = message.text
    await message.answer(
        text=vin,
        reply_markup=cancel_kb_inline()
        )


@service_router.callback_query(F.data == 'cancel_service')
async def user_process_cancel(call: CallbackQuery):
    await call.answer('Отмена сценария')
    await call.message.delete()
    await call.message.answer(
        text='Отмена операции.',
        reply_markup=user_kb_back()
    )
