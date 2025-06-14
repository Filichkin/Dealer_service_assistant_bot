from datetime import datetime, timedelta
from typing import Optional, List, Dict

from loguru import logger
from sqlalchemy import select, func, case
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from bot.dao.base import BaseDAO
from bot.dao.models import PartsData, Payment, Service, User, VehicleData


class UserDAO(BaseDAO[User]):
    model = User

    @classmethod
    async def get_purchase_statistics(
        cls, session: AsyncSession, telegram_id: int
    ) -> Optional[Dict[str, int]]:
        try:
            # Запрос для получения общего числа покупок и общей суммы.
            result = await session.execute(
                select(
                    func.count(Payment.id).label('count_payments'),
                    func.sum(Payment.price).label('total_amount')
                ).join(User).filter(User.telegram_id == telegram_id)
            )
            stats = result.one_or_none()

            if stats is None:
                return None

            count_payments, total_amount = stats
            return {
                'count_payments': count_payments,
                'total_amount': total_amount or 0
            }

        except SQLAlchemyError as e:
            # Обработка ошибок при работе с базой данных
            print(f'Ошибка при получении статистики покупок пользователя: {e}')
            return None

    @classmethod
    async def get_purchased_services(
        cls,
        session: AsyncSession,
        telegram_id: int
    ) -> Optional[List[Payment]]:
        try:
            # Запрос для получения пользователя с его оплатами.
            result = await session.execute(
                select(User)
                .options(
                    selectinload(User.payments).selectinload(Payment.service)
                )
                .filter(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if user is None:
                return None

            return user.payments

        except SQLAlchemyError as e:
            # Обработка ошибок при работе с базой данных
            print(
                f'Ошибка при получении информации об оплатах пользователя: {e}'
                )
            return None

    @classmethod
    async def get_payments(
        cls, session: AsyncSession, telegram_id: int
    ) -> Optional[List[Payment]]:
        try:
            # Запрос для получения пользователя с его покупками.
            result = await session.execute(
                select(User)
                .options(
                    selectinload(User.payments)
                )
                .filter(User.telegram_id == telegram_id)
            )
            user = result.scalar_one_or_none()

            if user is None:
                return None

            return user.payments

        except SQLAlchemyError as e:
            print(
                f'Ошибка при получении информации о покупках пользователя: {e}'
                )
            return None

    @classmethod
    async def get_statistics(cls, session: AsyncSession):
        try:
            now = datetime.now()

            query = select(
                func.count().label('total_users'),
                func.sum(
                    case(
                        (cls.model.created_at >= now - timedelta(days=1), 1),
                        else_=0
                        )
                    ).label('new_today'),
                func.sum(
                    case(
                        (cls.model.created_at >= now - timedelta(days=7), 1),
                        else_=0
                        )
                    ).label('new_week'),
                func.sum(
                    case(
                        (cls.model.created_at >= now - timedelta(days=30), 1),
                        else_=0
                        )
                    ).label('new_month')
            )

            result = await session.execute(query)
            stats = result.fetchone()

            statistics = {
                'total_users': stats.total_users,
                'new_today': stats.new_today,
                'new_week': stats.new_week,
                'new_month': stats.new_month
            }

            logger.info(f'Статистика успешно получена: {statistics}')
            return statistics
        except SQLAlchemyError as e:
            logger.error(f'Ошибка при получении статистики: {e}')
            raise


class PaymentDao(BaseDAO[Payment]):
    model = Payment

    @classmethod
    async def get_full_summ(cls, session: AsyncSession) -> int:
        query = select(func.sum(cls.model.price).label('total_price'))
        result = await session.execute(query)
        total_price = result.scalars().one_or_none()
        return total_price if total_price is not None else 0

    @classmethod
    async def get_actual_users_telegram_ids(
        cls,
        session: AsyncSession,
        service_id: int
    ):
        result = await session.execute(
            select(Payment).options(
                selectinload(Payment.user)
                ).filter(Payment.service_id == service_id
                         ).filter(Payment.expire > datetime.now())
        )
        payments = result.scalars().all()
        telegram_ids = [payment.user.telegram_id for payment in payments]
        return telegram_ids


class ServiceDao(BaseDAO[Service]):
    model = Service


class VehicleDao(BaseDAO[VehicleData]):
    model = VehicleData


class PartsDao(BaseDAO[VehicleData]):
    model = PartsData
