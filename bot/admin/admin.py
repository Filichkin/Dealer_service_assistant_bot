import asyncio

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram.types import CallbackQuery, Message
from sqlalchemy.ext.asyncio import AsyncSession

from bot.admin.kbs import (
    admin_kb,
    admin_kb_back,
    service_management_kb,
    cancel_kb_inline,
    admin_confirm_kb,
    dell_service_kb
)
from bot.admin.schemas import ServiceModel, ServiceIDModel
from bot.admin.utils import process_dell_text_msg
from bot.config import settings, bot
from bot.dao.dao import PaymentDao, ServiceDao, UserDAO
from bot.utils.parts_update_data import update_parts_data


admin_router = Router()


class AddService(StatesGroup):
    name = State()
    description = State()
    price = State()
    hidden_content = State()
    confirm_add = State()


@admin_router.message(
        Command(commands=['update'])
    )
async def cmd_update(message: Message, session_with_commit: AsyncSession):
    await update_parts_data(session_with_commit)


@admin_router.callback_query(
        F.data == 'admin_panel',
        F.from_user.id.in_(settings.ADMIN_IDS)
    )
async def start_admin(call: CallbackQuery):
    await call.answer('Доступ в админ-панель разрешен!')
    await call.message.edit_text(
        text='Вам разрешен доступ в админ-панель. '
        'Выберите необходимое действие.',
        reply_markup=admin_kb()
    )


@admin_router.callback_query(
        F.data == 'statistic',
        F.from_user.id.in_(settings.ADMIN_IDS)
        )
async def admin_statistic(
    call: CallbackQuery,
    session_without_commit: AsyncSession
):
    await call.answer('Запрос на получение статистики...')
    await call.answer('📊 Собираем статистику...')

    stats = await UserDAO.get_statistics(session=session_without_commit)
    total_summ = await PaymentDao.get_full_summ(session=session_without_commit)
    stats_message = (
        "📈 Статистика пользователей:\n\n"
        f"👥 Всего пользователей: {stats['total_users']}\n"
        f"🆕 Новых за сегодня: {stats['new_today']}\n"
        f"📅 Новых за неделю: {stats['new_week']}\n"
        f"📆 Новых за месяц: {stats['new_month']}\n\n"
        f"💰 Общая сумма заказов: {total_summ} руб.\n\n"
        "🕒 Данные актуальны на текущий момент."
    )
    await call.message.edit_text(
        text=stats_message,
        reply_markup=admin_kb()
    )


@admin_router.callback_query(
        F.data == 'cancel',
        F.from_user.id.in_(settings.ADMIN_IDS)
        )
async def admin_process_cancel(call: CallbackQuery, state: FSMContext):
    await state.clear()
    await call.answer('Отмена сценария добавления сервиса')
    await call.message.delete()
    await call.message.answer(
        text='Отмена добавления сервиса.',
        reply_markup=admin_kb_back()
    )


@admin_router.callback_query(
        F.data == 'delete_service',
        F.from_user.id.in_(settings.ADMIN_IDS)
        )
async def admin_process_start_dell(
    call: CallbackQuery,
    session_without_commit: AsyncSession
):
    await call.answer('Режим удаления сервисов')
    all_services = await ServiceDao.find_all(session=session_without_commit)

    await call.message.edit_text(
        text=f'На данный момент в базе данных {len(all_services)} сервисов. '
        f'Для удаления нажмите на кнопку ниже'
    )
    for service_data in all_services:

        service_text = (f'🛒 Описание севиса:\n\n'
                        f'🔹 <b>Название сервиса:</b> '
                        f'<b>{service_data.name}</b>\n'
                        f'🔹 <b>Описание:</b>\n\n<b>'
                        f'{service_data.description}</b>\n\n'
                        f'🔹 <b>Цена:</b> <b>{service_data.price} ₽</b>\n'
                        f'🔹 <b>Описание (закрытое):</b>\n\n<b>'
                        f'{service_data.hidden_content}</b>\n\n'
                        )
        await call.message.answer(
            text=service_text,
            reply_markup=dell_service_kb(service_data.id)
            )


@admin_router.callback_query(
        F.data.startswith('dell_'),
        F.from_user.id.in_(settings.ADMIN_IDS)
    )
async def admin_process_start_dell(
    call: CallbackQuery,
    session_with_commit: AsyncSession
):
    service_id = int(call.data.split('_')[-1])
    await ServiceDao.delete(
        session=session_with_commit,
        filters=ServiceIDModel(id=service_id)
        )
    await call.answer(f'Товар с ID {service_id} удален!', show_alert=True)
    await asyncio.sleep(1.5)
    await call.message.delete()


@admin_router.callback_query(
        F.data == 'process_services',
        F.from_user.id.in_(settings.ADMIN_IDS)
        )
async def admin_process_services(
    call: CallbackQuery,
    session_without_commit: AsyncSession
):
    await call.answer('Режим управления сервисами')
    all_services_count = await ServiceDao.count(session=session_without_commit)
    await call.message.edit_text(
        text=f'На данный момент в базе данных {all_services_count} сервисов.',
        reply_markup=service_management_kb()
    )


@admin_router.callback_query(
        F.data == 'add_service',
        F.from_user.id.in_(settings.ADMIN_IDS)
        )
async def admin_process_add_service(call: CallbackQuery, state: FSMContext):
    await call.answer('Запущен сценарий добавления сервиса.')
    await call.message.delete()
    msg = await call.message.answer(
        text='Для начала укажите название сервиса: ',
        reply_markup=cancel_kb_inline()
        )
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddService.name)


@admin_router.message(
        F.text,
        F.from_user.id.in_(settings.ADMIN_IDS),
        AddService.name
    )
async def admin_process_name(message: Message, state: FSMContext):
    await state.update_data(name=message.text)
    await process_dell_text_msg(message, state)
    msg = await message.answer(
        text='Дайте короткое описание сервиса: ',
        reply_markup=cancel_kb_inline()
        )
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddService.description)


@admin_router.message(
        F.text,
        F.from_user.id.in_(settings.ADMIN_IDS),
        AddService.description
        )
async def admin_process_description(
    message: Message,
    state: FSMContext,
):
    await state.update_data(description=message.html_text)
    await process_dell_text_msg(message, state)
    msg = await message.answer(
        text='Укажите стоимость сервиса: ',
        reply_markup=cancel_kb_inline()
        )
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddService.price)


@admin_router.message(
        F.text,
        F.from_user.id.in_(settings.ADMIN_IDS),
        AddService.price
    )
async def admin_process_price(message: Message, state: FSMContext):
    try:
        price = int(message.text)
        await state.update_data(price=price)
        await process_dell_text_msg(message, state)
        msg = await message.answer(
            text='Теперь отправьте контент, '
                 'который отобразится после покупки сервиса',
            reply_markup=cancel_kb_inline()
        )
        await state.update_data(last_msg_id=msg.message_id)
        await state.set_state(AddService.hidden_content)
    except ValueError:
        await message.answer(
            text='Ошибка! Необходимо ввести числовое значение для цены.'
            )
        return


@admin_router.message(
        F.text,
        F.from_user.id.in_(settings.ADMIN_IDS),
        AddService.hidden_content
        )
async def admin_process_hidden_content(
    message: Message,
    state: FSMContext
):
    await state.update_data(hidden_content=message.html_text)

    service_data = await state.get_data()

    service_text = (f'🛒 Проверьте, все ли корректно:\n\n'
                    f'🔹 <b>Название сервиса:</b> <b>'
                    f'{service_data["name"]}</b>\n'
                    f'🔹 <b>Описание:</b>\n\n<b>'
                    f'{service_data["description"]}</b>\n\n'
                    f'🔹 <b>Цена:</b> <b>{service_data["price"]} ₽</b>\n'
                    f'🔹 <b>Описание (закрытое):</b>\n\n<b>'
                    f'{service_data["hidden_content"]}</b>\n\n'
                    )
    await process_dell_text_msg(message, state)

    msg = await message.answer(
        text=service_text,
        reply_markup=admin_confirm_kb()
        )
    await state.update_data(last_msg_id=msg.message_id)
    await state.set_state(AddService.confirm_add)


@admin_router.callback_query(
        F.data == 'confirm_add',
        F.from_user.id.in_(settings.ADMIN_IDS)
        )
async def admin_process_confirm_add(
    call: CallbackQuery, state: FSMContext,
    session_with_commit: AsyncSession
):
    await call.answer('Приступаю к сохранению файла!')
    service_data = await state.get_data()
    await bot.delete_message(
        chat_id=call.from_user.id,
        message_id=service_data['last_msg_id']
        )
    del service_data['last_msg_id']
    await ServiceDao.add(
        session=session_with_commit,
        values=ServiceModel(**service_data)
        )
    await call.message.answer(
        text='Сервис успешно добавлен в базу данных!',
        reply_markup=admin_kb()
        )
