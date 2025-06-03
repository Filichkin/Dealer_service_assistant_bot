import argparse
import csv

import sqlalchemy
from sqlalchemy import MetaData
from sqlalchemy import insert

from bot.config import settings


parser = argparse.ArgumentParser()

parser.add_argument(
    '--csv_root',
    dest='file_path',
    required=True,
    help='path to csvfile'
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

parts_table = sqlalchemy.Table('maintenancedatas', metadata)


def json_upload(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        data = csv.reader(file)
        values = []
        for row in data:
            maintenance = {
                "vin": row[0],
                "type": row[1],
                "dealer_code": row[2],
                "maintenance_date": row[3],
                "odometer": row[4],
                }
            values.append(maintenance)

        with engine.connect() as conn:
            result = conn.execute(
                insert(parts_table),
                values
            )
            conn.commit()


if __name__ == '__main__':
    json_upload(args.file_path)
