from sqlalchemy.ext.asyncio import AsyncSession

from bot.dao.dao import PartsDao


async def parts_search(part: str, session_without_commit: AsyncSession):
    part = part.upper()
    result = await PartsDao.find_one_or_none_by_part(
        session=session_without_commit,
        part_number=part
        )
    if result is not None:
        return result
    return (
        'Информация о данном каталожном номере отсутствует '
        'или введена неверно!'
        )
