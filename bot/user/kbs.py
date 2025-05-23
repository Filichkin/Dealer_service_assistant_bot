from typing import List

from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    KeyboardButton,
    ReplyKeyboardMarkup
)
from aiogram.utils.keyboard import (
    InlineKeyboardBuilder,
)

from bot.config import settings
from bot.dao.models import Service


def main_user_kb(user_id: int) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text='👤 Мои сервисы', callback_data='my_profile')
    kb.button(text='🛍 Каталог', callback_data='catalog')
    kb.button(text='ℹ️ О сервисе', callback_data='about')
    kb.button(text='🌟 Поддержка 🌟', url='https://telegram.me/alexeyfill')
    if user_id in settings.ADMIN_IDS:
        kb.button(text='⚙️ Админ панель', callback_data='admin_panel')
    kb.adjust(2)
    return kb.as_markup()


'''
def main_user_kb(user_id: int) -> ReplyKeyboardMarkup:
    kb_list = [
        [
            KeyboardButton(text='👤 Мои сервисы', callback_data='my_profile'),
            KeyboardButton(text='🛍 Каталог', callback_data='catalog')
        ],
        [
            KeyboardButton(text='ℹ️ О сервисе', callback_data='about'),
            KeyboardButton(text='🌟 Поддержка 🌟', url='https://telegram.me/alexeyfill')
        ],
    ]
    if user_id in settings.ADMIN_IDS:
        kb_list.append(
            [
                KeyboardButton(
                    text='⚙️ Админ панель',
                    callback_data='admin_panel'
                    )
            ]
        )
    keyboard = ReplyKeyboardMarkup(
        keyboard=kb_list,
        resize_keyboard=True,
        one_time_keyboard=True,
        input_field_placeholder='Воспользуйтесь меню:'
    )
    return keyboard
'''


def catalog_kb(service_data: List[Service]) -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    for service in service_data:
        kb.button(text=service.name, callback_data=f'service_{service.id}')
    kb.button(text='🏠 На главную', callback_data='home')
    kb.adjust(2)
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
    kb.button(text='🛍 Назад', callback_data='catalog')
    kb.button(text='🏠 На главную', callback_data='home')
    kb.adjust(2)
    return kb.as_markup()


def get_service_buy_kb(price) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=f'Оплатить {price}₽', pay=True)],
        [InlineKeyboardButton(text='Отменить', callback_data='home')]
    ])
