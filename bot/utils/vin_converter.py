from sqlalchemy.ext.asyncio import AsyncSession

from bot.dao.dao import VehicleDao

prefix = ('Z', 'Z', 'U', 'M')


async def vin_converter(vin: str, session_without_commit: AsyncSession):
    vin = vin.upper()
    if len(vin) < 17:
        return 'Данный VIN введен не корректно'
    elif vin.startswith(prefix):
        return 'Данный VIN не имеет DKD аналога'
    try:
        result = VehicleDao.find_one_or_none(
            session=session_without_commit,
            filters=vin
            )
        return await result.dkd_vin
    except KeyError:
        return 'Данный VIN введен не корректно или отсутствует в базе данных'
