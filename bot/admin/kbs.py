from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


def admin_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='📊 Статистика', callback_data='statistic')
    kb.button(
        text='👨‍💼 Управлять сервисами',
        callback_data='process_services'
        )
    kb.button(text='🏠 На главную', callback_data='home')
    kb.adjust(2)
    return kb.as_markup()


def admin_kb_back() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='⚙️ Админ панель', callback_data='admin_panel')
    kb.button(text='🏠 На главную', callback_data='home')
    kb.adjust(1)
    return kb.as_markup()


def dell_service_kb(service_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='🗑️ Удалить', callback_data=f'dell_{service_id}')
    kb.button(text='⚙️ Админ панель', callback_data='admin_panel')
    kb.button(text='🏠 На главную', callback_data='home')
    kb.adjust(2, 2, 1)
    return kb.as_markup()


def service_management_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='➕ Добавить сервис', callback_data='add_service')
    kb.button(text='🗑️ Удалить сервис', callback_data='delete_service')
    kb.button(text='⚙️ Админ панель', callback_data='admin_panel')
    kb.button(text='🏠 На главную', callback_data='home')
    kb.adjust(2, 2, 1)
    return kb.as_markup()


def cancel_kb_inline() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Отмена', callback_data='cancel')
    return kb.as_markup()


def admin_confirm_kb() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='Все верно', callback_data='confirm_add')
    kb.button(text='Отмена', callback_data='admin_panel')
    kb.adjust(1)
    return kb.as_markup()
