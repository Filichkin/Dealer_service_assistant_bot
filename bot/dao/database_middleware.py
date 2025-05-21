from typing import Callable, Dict, Any, Awaitable

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from bot.dao.database import async_session_maker


class BaseDatabaseMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[
            [Message | CallbackQuery, Dict[str, Any]], Awaitable[Any]
            ],
        event: Message | CallbackQuery,
        data: Dict[str, Any]
    ) -> Any:
        async with async_session_maker() as session:
            self.set_session(data, session)  # Устанавливаем сессию
            try:
                result = await handler(event, data)  # Обрабатываем событие
                # Дополнительные действия (например, коммит)
                await self.after_handler(session)
                return result
            except Exception as e:
                await session.rollback()  # Откат изменений в случае ошибки
                raise e
            finally:
                await session.close()  # Закрываем сессию

    def set_session(self, data: Dict[str, Any], session) -> None:
        """
        Метод для установки сессии в данные.
        Реализуется в дочерних классах.
        """
        raise NotImplementedError(
            'Этот метод должен быть реализован в подклассах.'
            )

    async def after_handler(self, session) -> None:
        """
        Метод для выполнения действий после обработки события.
        По умолчанию ничего не делает.
        """
        pass


class DatabaseMiddlewareWithoutCommit(BaseDatabaseMiddleware):
    def set_session(self, data: Dict[str, Any], session) -> None:
        data['session_without_commit'] = session


class DatabaseMiddlewareWithCommit(BaseDatabaseMiddleware):
    def set_session(self, data: Dict[str, Any], session) -> None:
        data['session_with_commit'] = session

    async def after_handler(self, session) -> None:
        await session.commit()
