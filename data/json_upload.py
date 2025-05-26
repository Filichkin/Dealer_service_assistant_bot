import json

import sqlalchemy
from sqlalchemy import MetaData
from sqlalchemy import insert

from bot.config import settings


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

PATH = 'data/test.json'


def json_upload(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        values = []
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

        with engine.connect() as conn:
            result = conn.execute(
                insert(vehicle_table),
                values
            )
            conn.commit()


if __name__ == '__main__':
    json_upload(PATH)
