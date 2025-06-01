from sqlalchemy.ext.asyncio import AsyncSession

from bot.dao.dao import PaymentDao


async def get_permission(service_id, session_without_commit: AsyncSession):
    telegram_ids = await PaymentDao.get_users_telegram_ids(
            session=session_without_commit,
            service_id=service_id
            )
    return telegram_ids
