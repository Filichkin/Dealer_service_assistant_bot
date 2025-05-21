import asyncio

from aiogram import Router, F
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
from bot.admin.schemas import PaymentModel, PaymentIDModelIDModel
from bot.admin.utils import process_dell_text_msg
from bot.config import settings, bot
from bot.dao.dao import PaymentDao, ServiceDao, UserDAO


admin_router = Router()


class AddService(StatesGroup):
    name = State()
    description = State()
    price = State()
    hidden_content = State()
    confirm_add = State()


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
        F.data == 'process_services',
        F.from_user.id.in_(settings.ADMIN_IDS)
        )
async def admin_process_products(
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
