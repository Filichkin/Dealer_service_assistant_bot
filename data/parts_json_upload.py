import argparse
import json

from loguru import logger
import sqlalchemy
from sqlalchemy import MetaData
from sqlalchemy import insert

from bot.config import settings


parser = argparse.ArgumentParser()

parser.add_argument(
    '--json_root',
    dest='file_path',
    required=True,
    help='path to json file'
    )

args = parser.parse_args()


DATABASE_URL = (f'postgresql://{settings.POSTGRES_USER}:'
                f'{settings.POSTGRES_PASSWORD}@'
                f'{settings.POSTGRES_HOST}:{settings.DATABASE_PORT}/'
                f'{settings.POSTGRES_DB}'
                )

engine = sqlalchemy.create_engine(DATABASE_URL)

metadata = MetaData()
metadata.drop_all(engine)
metadata.create_all(engine)
metadata.reflect(engine)

parts_table = sqlalchemy.Table('partsdatas', metadata)


def json_upload(file_path):
    logger.info('Начало загрузки данных в БД.')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            values = []
            part_count = 0
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
                part_count += 1

            with engine.connect() as conn:
                result = conn.execute(
                    insert(parts_table),
                    values
                )
                conn.commit()
        logger.info(f'Загруженно в БД {part_count} позиций.')
    except Exception as error:
        logger.error(
            f'Ошибка при загрузке данных: {error}'
            )
        return None


if __name__ == '__main__':
    json_upload(args.file_path)
