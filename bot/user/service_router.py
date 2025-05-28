from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import (
    CallbackQuery,
    Message
)
from sqlalchemy.ext.asyncio import AsyncSession

from bot.dao.dao import PaymentDao, ServiceDao
from bot.user.kbs import (
    cancel_kb_inline,
    cancel_convert_kb_inline,
    user_kb_back
)
from bot.utils.vin_converter import vin_converter


service_router = Router()


class AddMessage(StatesGroup):
    data = State()


@service_router.callback_query(
        F.data.startswith('user_service_')
    )
async def page_service(
    call: CallbackQuery,
    session_without_commit: AsyncSession
):
    service_id = int(call.data.split('_')[-1])
    payments = await PaymentDao.get_users_ids(
        session=session_without_commit,
        service_id=service_id
        )
    print([payment.user.telegram_id for payment in payments])
    service = await ServiceDao.find_one_or_none_by_id(
        session=session_without_commit,
        data_id=service_id
    )
    if 'VIN' in str(service.name):
        await call.answer('Запущен VIN decoder.')
        service_text = (
            'Введите команду convert'
        )
        await call.message.answer(
            service_text,
            reply_markup=cancel_convert_kb_inline()
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
        Command(commands=['convert'])
    )
async def convert_handler(message: Message):
    await message.answer(text='Введите локальный VIN')


@service_router.message()
async def vin_decoder(
    message: Message,
    session_without_commit: AsyncSession
):
    local_vin = message.text
    convert_result = await vin_converter(local_vin, session_without_commit)
    if isinstance(convert_result, str):
        await message.answer(
            text=convert_result,
            reply_markup=cancel_convert_kb_inline()
            )
    else:
        await message.answer(
            text=convert_result.dkd_vin,
            reply_markup=cancel_convert_kb_inline()
            )


@service_router.callback_query(F.data == 'cancel_service')
async def user_process_cancel(call: CallbackQuery):
    await call.answer('Отмена сценария')
    await call.message.delete()
    await call.message.answer(
        text='Отмена операции.',
        reply_markup=user_kb_back()
    )


@service_router.callback_query(F.data == 'convert_service')
async def user_process_convert(call: CallbackQuery):
    await convert_handler(message=call.message)
