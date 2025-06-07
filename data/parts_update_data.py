import json

from loguru import logger

from bot.dao.dao import PartsDao
from bot.dao.session_maker import session_manager


@session_manager.connection(commit=True)
async def update_parts_data(session):
    logger.info('Начало обновления данных в БД.')
    try:
        with open('data/merged_parts.json', 'r', encoding='utf-8') as file:
            data = json.load(file)
            values = []
            for item in data:
                part = {
                    "part_number": item,
                    "model": data[item][0],
                    "descriprion_en": data[item][1],
                    "descriprion_ru": data[item][2],
                    "dnp": data[item][3],
                    "list_price": data[item][4],
                    "mobis_count": data[item][5],
                    "ellias_count": data[item][6],
                    }
                values.append(part)
        return await PartsDao.bulk_update_parts_data(
            session=session,
            records=values
            )

    except Exception as error:
        logger.error(
            f'Ошибка при загрузке данных: {error}'
            )
        return None
