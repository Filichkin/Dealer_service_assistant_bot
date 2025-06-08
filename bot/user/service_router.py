from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    CallbackQuery,
    Message
)
from sqlalchemy.ext.asyncio import AsyncSession

from bot.dao.dao import ServiceDao
from bot.user.kbs import (
    cancel_convert_kb_inline,
    cancel_maintenance_kb_inline,
    cancel_search_kb_inline,
    cancel_warranty_kb_inline,
    user_kb_back
)
from bot.user.constants import (
    ASSISTANT_SERVICE_ID,
    MAINTENANCE_SERVICE_ID,
    PARTS_SEARCH_SERVICE_ID,
    VIN_DECODER_SERVICE_ID
)
from bot.user.permissions import get_permission
from bot.user.states import (
    AssistantSteps,
    MaintenanceSteps,
    PartSteps,
    VinSteps
)
from bot.utils.parts_data import parts_search
from bot.utils.vin_converter import vin_converter
from bot.utils.assistant import assistant_service


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
    if 'VIN конвертер' in str(service.name):
        await call.answer('Запущен VIN конвертер.')
        service_text = (
            'Введите команду 🔍 Convert'
        )
        await call.message.answer(
            service_text,
            reply_markup=cancel_convert_kb_inline()
        )

    elif 'Проверка наличия запасных частей' in str(service.name):
        await call.answer(
            'Запущен сервис для проверки наличия запасных частей.'
            )
        service_text = (
            'Введите команду ⚙️ Parts'
        )
        await call.message.answer(
            service_text,
            reply_markup=cancel_search_kb_inline()
        )
    elif 'Проверка истории ТО' in str(service.name):
        await call.answer('Запущен сервис для проверки истории ТО.')
        service_text = (
            'Введите команду 🛠 Maintenance'
        )
        await call.message.answer(
            service_text,
            reply_markup=cancel_maintenance_kb_inline()
        )
    elif 'Ассистент по гарантии' in str(service.name):
        await call.answer('Запущен ассистент по гарантии.')
        service_text = (
            'Введите команду 🤖 Assistant'
        )
        await call.message.answer(
            service_text,
            reply_markup=cancel_warranty_kb_inline()
        )
    else:
        await call.answer('О данном сервисе нет информации.')


@service_router.message(
        Command(commands=['convert'])
    )
async def convert_handler(
    message: Message,
    state: FSMContext
):
    await message.answer(text='Введите локальный VIN')
    await state.set_state(VinSteps.vin)


@service_router.message(VinSteps.vin)
async def process_vin(
    message: Message,
    state: FSMContext,
    session_without_commit: AsyncSession
):
    if not await get_permission(
        VIN_DECODER_SERVICE_ID,
        message.from_user.id,
        session_without_commit
    ):
        return await message.answer(
            text='Сервис не оплачен или закончилась подписка'
            )
    await state.update_data(vin=message.text)
    vin = await state.get_data()
    local_vin = vin['vin']
    convert_result = await vin_converter(local_vin, session_without_commit)
    if isinstance(convert_result, str):
        await message.answer(
            text=convert_result
            )
        await message.answer(
            text='Для новой проверки повторите команду 🔍 Convert',
            reply_markup=cancel_convert_kb_inline()
            )
    else:
        await message.answer(
            text=convert_result.dkd_vin
            )
        await message.answer(
            text='Для новой проверки повторите команду 🔍 Convert',
            reply_markup=cancel_convert_kb_inline()
            )
    await state.clear()


@service_router.message(
        Command(commands=['parts'])
    )
async def parts_handler(message: Message, state: FSMContext):
    await message.answer(text='Введите каталожный номер')
    await state.set_state(PartSteps.part_number)


@service_router.message(PartSteps.part_number)
async def process_part_number(
    message: Message,
    state: FSMContext,
    session_without_commit: AsyncSession
):
    if not await get_permission(
        PARTS_SEARCH_SERVICE_ID,
        message.from_user.id,
        session_without_commit
    ):
        return await message.answer(
            text='Сервис не оплачен или закончилась подписка'
            )
    await state.update_data(part_number=message.text)
    part_number = await state.get_data()
    part_number = part_number['part_number']
    search_result = await parts_search(part_number, session_without_commit)
    if isinstance(search_result, str):
        await message.answer(
            text=search_result
            )
        await message.answer(
            text='Для новой проверки повторите команду ⚙️ Parts',
            reply_markup=cancel_search_kb_inline()
            )
    else:
        parts_text = (
            f'<b>{part_number.upper()}</b>\n'
            f'<b>{search_result.descriprion_en}</b>\n\n'
            f'Mobis: {search_result.mobis_count} \n'
            f'Ellias: {search_result.ellias_count}\n'
            )

        await message.answer(
            text=parts_text
            )
        await message.answer(
            text='Для новой проверки повторите команду ⚙️ Parts',
            reply_markup=cancel_search_kb_inline()
            )
    await state.clear()


@service_router.message(
        Command(commands=['maintenance'])
    )
async def maintenance_handler(message: Message, state: FSMContext):
    await message.answer(text='Введите VIN')
    await state.set_state(MaintenanceSteps.vin)


@service_router.message(MaintenanceSteps.vin)
async def process_maintenance(
    message: Message,
    state: FSMContext,
    session_without_commit: AsyncSession
):
    if not await get_permission(
        MAINTENANCE_SERVICE_ID,
        message.from_user.id,
        session_without_commit
    ):
        return await message.answer(
            text='Сервис не оплачен или закончилась подписка'
            )
    await state.update_data(vin=message.text)
    vin = await state.get_data()
    vin = vin['vin']
    await message.answer(
            text=f'Сервис в разработке: {vin}'
            )
    await message.answer(
            text='Для новой проверки повторите команду 🛠 Maintenance',
            reply_markup=cancel_maintenance_kb_inline()
            )
    await state.clear()


@service_router.message(
        Command(commands=['assistant'])
    )
async def assistant_handler(message: Message, state: FSMContext):
    await message.answer(text='Введите ваш вопрос')
    await state.set_state(AssistantSteps.prompt)


@service_router.message(AssistantSteps.prompt)
async def process_assistant(
    message: Message,
    state: FSMContext,
    session_without_commit: AsyncSession
):
    if not await get_permission(
        ASSISTANT_SERVICE_ID,
        message.from_user.id,
        session_without_commit
    ):
        return await message.answer(
            text='Сервис не оплачен или закончилась подписка'
            )
    await state.update_data(prompt=message.text)
    prompt = await state.get_data()
    prompt = prompt['prompt']
    await message.answer(text=(
        'Уже ищу информацию...\n'
        'Время поиска может составлять более 30 секунд...'
        )
    )
    result = assistant_service(prompt)
    await message.answer(text=('Вот что мне удалось найти:'))
    try:
        await message.answer(
                text=result,
                parse_mode='Markdown'
                )
    except TelegramBadRequest:
        await message.answer(
                text=result,
                parse_mode='HTML'
                )
    await message.answer(
            text='Для новой проверки повторите команду 🤖 Assistant',
            reply_markup=cancel_warranty_kb_inline()
            )
    await state.clear()


@service_router.callback_query(F.data == 'cancel_service')
async def user_process_cancel(call: CallbackQuery):
    await call.answer('Отмена сценария')
    await call.message.answer(
        text='Выберите необходимое действие:',
        reply_markup=user_kb_back()
    )


@service_router.callback_query(F.data == 'convert_service')
async def user_process_convert(call: CallbackQuery, state: FSMContext):
    await convert_handler(message=call.message, state=state)


@service_router.callback_query(F.data == 'parts_service')
async def user_process_parts(call: CallbackQuery, state: FSMContext):
    await parts_handler(message=call.message, state=state)


@service_router.callback_query(F.data == 'maintenance_service')
async def user_process_maintenance(call: CallbackQuery, state: FSMContext):
    await maintenance_handler(message=call.message, state=state)


@service_router.callback_query(F.data == 'assistant_service')
async def user_process_assistant(call: CallbackQuery, state: FSMContext):
    await assistant_handler(message=call.message, state=state)
