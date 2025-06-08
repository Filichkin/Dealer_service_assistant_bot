from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.types import Message, CallbackQuery
from sqlalchemy.ext.asyncio import AsyncSession

from bot.dao.dao import UserDAO
from bot.user.kbs import main_user_kb, payments_kb, user_services_kb
from bot.user.schemas import TelegramIDModel, UserModel


user_router = Router()


@user_router.message(CommandStart())
async def cmd_start(message: Message, session_with_commit: AsyncSession):
    user_id = message.from_user.id
    user_info = await UserDAO.find_one_or_none(
        session=session_with_commit,
        filters=TelegramIDModel(telegram_id=user_id)
    )

    if user_info:
        return await message.answer(
            'Выберите необходимое действие:',
            reply_markup=main_user_kb(user_id)
        )

    values = UserModel(
        telegram_id=user_id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
        last_name=message.from_user.last_name,
    )
    await UserDAO.add(session=session_with_commit, values=values)
    await message.answer(
        '<b>Благодарим за использование бота!</b>. '
        'Выберите необходимое действие.',
        reply_markup=main_user_kb(user_id)
    )


@user_router.callback_query(F.data == 'home')
async def page_home(call: CallbackQuery):
    await call.answer('Главная страница')
    return await call.message.answer(
        'Выберите необходимое действие:',
        reply_markup=main_user_kb(call.from_user.id)
    )


@user_router.callback_query(F.data == 'about')
async def page_about(call: CallbackQuery):
    await call.answer('О сервисах')
    await call.message.answer(
        text=(
            '*Здесь вы можете: *\n\n'
            '🚗 Получить оригинальный VIN\n\n'
            '🛞 Узнать наличие запасной части по артикулу\n\n'
            '⚙️ Проверить историю ТО\n\n'
            '🤖 Задать вопрос ассистенту по гарантии\n\n'
            '📩 Задать вопрос разработчику\n\n'
            '_Для оплаты подписки на сервис, '
            'перейдите в каталог._\n'
        ),
        parse_mode='Markdown',
        reply_markup=call.message.reply_markup
    )


@user_router.callback_query(F.data == 'my_profile')
async def page_user_profile(
    call: CallbackQuery,
    session_without_commit: AsyncSession
):
    await call.answer('Профиль')

    # Получаем покупки пользователя
    payments = await UserDAO.get_purchased_services(
            session=session_without_commit,
            telegram_id=call.from_user.id
            )
    # Формируем сообщение в зависимости от наличия покупок
    if len(payments) == 0:
        await call.message.answer(
            text='🔍 <b>У вас пока нет оплаченных подписок.</b>\n\n'
                 'Откройте каталог и выберите нужный сервис!',
            reply_markup=main_user_kb(call.from_user.id)
        )
    else:
        # Формируем список оплаченных сервисов.
        services = [payment.service for payment in payments]
        await call.message.edit_text(
            text='Ваши оплаченные сервисы:',
            reply_markup=user_services_kb(services)
        )


@user_router.callback_query(F.data == 'payments')
async def page_user_payments(
    call: CallbackQuery,
    session_without_commit: AsyncSession
):
    await call.answer('Мои оплаты')

    # Получаем список покупок пользователя.
    payments = await UserDAO.get_purchased_services(
        session=session_without_commit,
        telegram_id=call.from_user.id
        )
    payments_statistic = await UserDAO.get_purchase_statistics(
        session=session_without_commit,
        telegram_id=call.from_user.id
        )
    total_amount = payments_statistic.get('total_amount', 0)
    total_payments = payments_statistic.get('count_payments', 0)

    if not payments:
        await call.message.edit_text(
            text='🔍 <b>У вас пока нет оплаченных подписок.</b>\n\n'
                 'Откройте каталог и выберите необходимый сервис!',
            reply_markup=main_user_kb(call.from_user.id)
        )
        return
    statistic_text = (
            f'🚗  <b>Ваш профиль:</b>\n\n'
            f'Количество подписок: <b>{total_payments}</b>\n'
            f'Общая сумма: <b>{total_amount}₽</b>\n\n'
        )
    await call.message.answer(text=statistic_text)
    await call.message.answer(
        text='Для получения деталей по платежам или выхода, '
        'выберите необходимое действие:',
        reply_markup=payments_kb()
    )


@user_router.callback_query(F.data == 'payments_details')
async def page_user_payments_details(
    call: CallbackQuery,
    session_without_commit: AsyncSession
):
    await call.answer('Детали оплат:')

    # Получаем список покупок пользователя.
    payments = await UserDAO.get_purchased_services(
        session=session_without_commit,
        telegram_id=call.from_user.id
        )
    # Для каждой оплаты отправляем информацию.
    for payment in payments:
        service = payment.service

        service_text = (
            f'🛒 <b>Информация о ваших оплаченных подписках:</b>\n'
            f'━━━━━━━━━━━━━━━━━━\n'
            f'<b>Название:</b> <i>{service.name}</i>\n'
            f'<b>Описание:</b>\n<i>{service.description}</i>\n'
            f'<b>Цена:</b> <b>{service.price} ₽</b>\n'
            f' <b>Срок действия до:</b>\n<i>'
            f'{payment.expire.strftime("%Y-%m-%d-%H:%M:%S")}</i>\n'
            f"━━━━━━━━━━━━━━━━━━\n"
        )
        await call.message.answer(text=service_text)

    await call.message.answer(
        text='Для продолжения работы, выберите необходимое действие:',
        reply_markup=main_user_kb(call.from_user.id)
    )
