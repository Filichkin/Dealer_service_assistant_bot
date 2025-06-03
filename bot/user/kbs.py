from typing import List

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
)

from bot.config import settings
from bot.dao.models import Service


def main_user_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='ℹ️ О сервисах', callback_data='about')
    kb.button(text='🗂 Каталог', callback_data='catalog')
    kb.button(text='🚗 Личный кабинет', callback_data='my_profile')
    kb.button(text='👤 Написать в поддержку', url=settings.SUPPORT_URL)
    if user_id in settings.ADMIN_IDS:
        kb.button(text='⚙️ Админ панель', callback_data='admin_panel')
    kb.adjust(1)
    return kb.as_markup()


def catalog_kb(service_data: List[Service]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for service in service_data:
        kb.button(text=service.name, callback_data=f'service_{service.id}')
    kb.button(text='🏠 На главную', callback_data='home')
    kb.adjust(1)
    return kb.as_markup()


def user_services_kb(service_data: List[Service]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for service in service_data:
        kb.button(
            text=service.name,
            callback_data=f'user_service_{service.id}'
            )
    kb.button(text='💳 История платежей', callback_data='payments')
    kb.button(text='🏠 На главную', callback_data='home')
    kb.adjust(1)
    return kb.as_markup()


def payments_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='🗑 Смотреть платежи', callback_data='payments')
    kb.button(text='🏠 На главную', callback_data='home')
    kb.adjust(1)
    return kb.as_markup()


def service_kb(service_id, price) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='💸 Оплатить', callback_data=f'pay_{service_id}_{price}')
    kb.button(text='🗂 В каталог', callback_data='catalog')
    kb.button(text='🏠 На главную', callback_data='home')
    kb.adjust(2)
    return kb.as_markup()


def get_service_buy_kb(price) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'Оплатить {price}₽', pay=True)],
        [InlineKeyboardButton(text='Отменить', callback_data='home')]
    ])


def home_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='🏠 На главную', callback_data='home')
    kb.adjust(1)
    return kb.as_markup()


def cancel_kb_inline() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Выйти', callback_data='cancel_service')
    return kb.as_markup()


def cancel_convert_kb_inline() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Convert', callback_data='convert_service')
    kb.button(text='Выйти', callback_data='cancel_service')
    return kb.as_markup()


def cancel_search_kb_inline() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Search', callback_data='search_service')
    kb.button(text='Выйти', callback_data='cancel_service')
    return kb.as_markup()


def cancel_maintenance_kb_inline() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Maintenance', callback_data='maintenance_service')
    kb.button(text='Выйти', callback_data='cancel_service')
    return kb.as_markup()


def cancel_warranty_kb_inline() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Warranty', callback_data='warranty_service')
    kb.button(text='Выйти', callback_data='cancel_service')
    return kb.as_markup()


def user_kb_back() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='🏠 На главную', callback_data='home')
    kb.button(text='🚗 Мои сервисы', callback_data='my_profile')
    kb.adjust(1)
    return kb.as_markup()
