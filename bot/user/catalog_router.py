from datetime import datetime, timedelta

from aiogram import Router, F
from aiogram.enums import ContentType
from aiogram.types import (
    Message,
    CallbackQuery,
    LabeledPrice,
    PreCheckoutQuery
)
from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from bot.config import bot, settings
from bot.dao.dao import UserDAO, ServiceDao, PaymentDao
from bot.user.kbs import (
    main_user_kb,
    catalog_kb,
    service_kb,
    get_service_buy_kb
)
from bot.user.schemas import TelegramIDModel, PaymentData


catalog_router = Router()


@catalog_router.callback_query(F.data == 'catalog')
async def page_catalog(
    call: CallbackQuery,
    session_without_commit: AsyncSession
):
    await call.answer('Загрузка каталога...')
    catalog_data = await ServiceDao.find_all(session=session_without_commit)

    await call.message.edit_text(
        text='Выберите сервис:',
        reply_markup=catalog_kb(catalog_data)
    )


@catalog_router.callback_query(F.data.startswith('service_'))
async def page_service(
    call: CallbackQuery,
    session_without_commit: AsyncSession
):
    service_id = int(call.data.split('_')[-1])
    service = await ServiceDao.find_one_or_none_by_id(
        session=session_without_commit,
        data_id=service_id
    )
    if service:
        service_text = (
            f'📦 <b>Название сервиса:</b> {service.name}\n\n'
            f'💰 <b>Цена:</b> {service.price} руб.\n\n'
            f'📝 <b>Описание:</b>\n<i>{service.description}</i>\n\n'
            f'━━━━━━━━━━━━━━━━━━'
        )
        await call.message.answer(
            service_text,
            reply_markup=service_kb(service.id, service.price)
        )
    else:
        await call.answer('О данном сервисе нет информации.')


@catalog_router.callback_query(F.data.startswith('pay_'))
async def process_about(
    call: CallbackQuery,
    session_without_commit: AsyncSession
):
    user_info = await UserDAO.find_one_or_none(
        session=session_without_commit,
        filters=TelegramIDModel(telegram_id=call.from_user.id)
    )
    _, service_id, price = call.data.split('_')
    telegram_ids = await PaymentDao.get_actual_users_telegram_ids(
            session=session_without_commit,
            service_id=int(service_id)
            )
    if user_info.telegram_id in telegram_ids:
        return await bot.send_message(
            chat_id=call.from_user.id,
            text='❗️ У вас уже есть актуальная подписка на данный сервис'
            )

    await bot.send_invoice(
        chat_id=call.from_user.id,
        title=f'Оплата 👉 {price}₽',
        description=(
            f'Пожалуйста, завершите оплату в размере {price}₽, '
            f'чтобы открыть доступ к выбранному сервису.'
            ),
        payload=f'{user_info.id}_{service_id}',
        provider_token=settings.PROVIDER_TOKEN,
        currency='rub',
        prices=[
            LabeledPrice(
                label=f'Оплата {price}',
                amount=int(price) * 100
                )
            ],
        reply_markup=get_service_buy_kb(price)
    )


@catalog_router.pre_checkout_query(lambda query: True)
async def pre_checkout_query(pre_checkout_q: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_q.id, ok=True)


@catalog_router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def successful_payment(
    message: Message,
    session_with_commit: AsyncSession
):
    payment_info = message.successful_payment
    user_id, service_id = payment_info.invoice_payload.split('_')
    expire = datetime.now() + timedelta(
            minutes=settings.PAYMENT_EXPIRE_MINUTES
            )
    payment_data = {
        'user_id': int(user_id),
        'payment_id': payment_info.telegram_payment_charge_id,
        'price': payment_info.total_amount / 100,
        'service_id': int(service_id),
        'expire': expire
    }
    print(payment_data)
    # Добавляем информацию о покупке в базу данных
    await PaymentDao.add(
        session=session_with_commit,
        values=PaymentData(**payment_data)
        )
    service_data = await ServiceDao.find_one_or_none_by_id(
        session=session_with_commit,
        data_id=int(service_id)
        )

    # Формируем уведомление администраторам
    for admin_id in settings.ADMIN_IDS:
        try:
            username = message.from_user.username
            user_info = (
                f'@{username} ({message.from_user.id})'
                if username else f'c ID {message.from_user.id}'
                )

            await bot.send_message(
                chat_id=admin_id,
                text=(
                    f'💲 Пользователь {user_info} оплатил сервис '
                    f'<b>{service_data.name}</b> (ID: {service_id}) '
                    f'в размере <b>{service_data.price} ₽</b>.'
                )
            )
        except Exception as e:
            logger.error(
                f'Ошибка при отправке уведомления администраторам: {e}'
                )

    # Подготавливаем текст для пользователя
    service_text = (
        f'🎉 <b>Спасибо за покупку!</b>\n\n'
        f'🛒 <b>Информация о вашем сервисе:</b>\n'
        f"━━━━━━━━━━━━━━━━━━\n"
        f'🔹 <b>Название:</b> <b>{service_data.name}</b>\n'
        f'🔹 <b>Описание:</b>\n<i>{service_data.description}</i>\n'
        f'🔹 <b>Цена:</b> <b>{service_data.price} ₽</b>\n'
        f'🔹 <b>Закрытое описание:</b>\n<i>{service_data.hidden_content}</i>\n'
        f'━━━━━━━━━━━━━━━━━━\n'
        f'ℹ️ <b>Информацию о всех ваших покупках '
        f'вы можете найти в личном профиле.</b>'
    )

    # Отправляем информацию о товаре пользователю
    await message.answer(
        text=service_text,
        reply_markup=main_user_kb(message.from_user.id)
    )
