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

vehicle_table = sqlalchemy.Table('vehicledatas', metadata)


def json_upload(file_path):
    logger.info('Начало загрузки данных в БД.')
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            data = json.load(file)
            values = []
            vin_count = 0
            for item in data:
                vehicle = {
                    "local_vin": item,
                    "dkd_vin": data[item][0],
                    "dist_code": data[item][1],
                    "warranty_start_date": data[item][2],
                    "engine_number": data[item][3],
                    "transmission_number": data[item][4],
                    "key_number": data[item][5],
                    "body_color": data[item][6]
                    }
                values.append(vehicle)
                vin_count += 1

            with engine.connect() as conn:
                result = conn.execute(
                    insert(vehicle_table),
                    values
                )
                conn.commit()
        logger.info(f'Загруженно в БД {vin_count} позиций.')
    except Exception as error:
        logger.error(
            f'Ошибка при загрузке данных: {error}'
            )
        return None


if __name__ == '__main__':
    json_upload(args.file_path)
