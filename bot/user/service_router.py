from aiogram import Router, F
from aiogram.types import (
    CallbackQuery,
    Message
)
from sqlalchemy.ext.asyncio import AsyncSession

from bot.dao.dao import ServiceDao
from bot.user.kbs import cancel_kb_inline, user_kb_back
from bot.utils.vin_converter import vin_converter


prefix = ('Z', 'Z', 'U', 'M')

service_router = Router()


@service_router.callback_query(
        F.data.startswith('user_service_')
    )
async def page_service(
    call: CallbackQuery,
    session_without_commit: AsyncSession
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

    elif 'Наличие запасных частей' in str(service.name):
        await call.answer('Запущена проверка наличия запасных частей.')
        service_text = (
            'Введите каталожный номер'
        )
        await call.message.answer(
            service_text,
            reply_markup=cancel_kb_inline()
        )
    elif 'История ТО' in str(service.name):
        await call.answer('Запущена проверка истории ТО.')
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
        F.text.len() == 17,
        F.from_user.id.in_({312831871})
    )
async def vin_decoder(message: Message, session_without_commit: AsyncSession):
    vin = message.text.upper()
    if len(vin) < 17:
        return await message.answer(
            text='Данный VIN введен не корректно',
            reply_markup=cancel_kb_inline()
            )
    elif vin.startswith(prefix):
        return await message.answer(
            text='Данный VIN не имеет DKD аналога',
            reply_markup=cancel_kb_inline()
            )
    dkd = await vin_converter(vin, session_without_commit)
    await message.answer(
        text=dkd.dkd_vin,
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
