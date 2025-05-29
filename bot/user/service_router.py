from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    Message
)
from sqlalchemy.ext.asyncio import AsyncSession

from bot.dao.dao import PaymentDao, ServiceDao
from bot.user.kbs import (
    cancel_kb_inline,
    cancel_convert_kb_inline,
    cancel_search_kb_inline,
    user_kb_back
)
from bot.utils.parts_data import parts_search
from bot.utils.vin_converter import vin_converter


service_router = Router()


@service_router.callback_query(
        F.data.startswith('user_service_')
    )
async def page_service(
    call: CallbackQuery,
    session_without_commit: AsyncSession
):
    service_id = int(call.data.split('_')[-1])
    telegram_ids = await PaymentDao.get_users_telegram_ids(
        session=session_without_commit,
        service_id=service_id
        )
    print(telegram_ids)
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
            'Введите команду search'
        )
        await call.message.answer(
            service_text,
            reply_markup=cancel_search_kb_inline()
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


@service_router.message(F.text)
async def vin_decoder(
    message: Message,
    session_without_commit: AsyncSession
):
    telegram_ids = await PaymentDao.get_users_telegram_ids(
            session=session_without_commit,
            service_id=1
            )
    if message.from_user.id not in telegram_ids:
        return await message.answer(
            text='Сервис не оплачен'
            )
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


@service_router.message(
        Command(commands=['search'])
    )
async def search_handler(message: Message):
    await message.answer(text='Введите каталожный номер')


@service_router.message(F.text)
async def parts_data(
    message: Message,
    session_without_commit: AsyncSession
):
    telegram_ids = await PaymentDao.get_users_telegram_ids(
            session=session_without_commit,
            service_id=3
            )
    if message.from_user.id not in telegram_ids:
        return await message.answer(
            text='Сервис не оплачен'
            )
    part_number = message.text
    search_result = await parts_search(part_number, session_without_commit)
    if isinstance(search_result, str):
        await message.answer(
            text=search_result,
            reply_markup=cancel_search_kb_inline()
            )
    else:
        parts_text = (
            f'<b>{part_number.upper()}</b>\n\n'
            f'<b>{search_result.descriprion}</b>\n'
            f'━━━━━━━━━━━━━━━━━━\n'
            f'Mobis: {search_result.mobis_count} \n'
            f'Ellias: {search_result.ellias_count}\n'
            f'━━━━━━━━━━━━━━━━━━\n'
            )

        await message.answer(
            text=parts_text,
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


@service_router.callback_query(F.data == 'search_service')
async def user_process_search(call: CallbackQuery):
    await search_handler(message=call.message)
