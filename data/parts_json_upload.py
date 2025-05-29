import argparse
import json

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
    with open(file_path, 'r', encoding='utf-8') as file:
        data = json.load(file)
        values = []
        for item in data:
            part = {
                "part_number": item,
                "descriprion": data[item][0],
                "ellias_count": data[item][1],
                "mobis_count": data[item][2],
                }
            values.append(part)

        with engine.connect() as conn:
            result = conn.execute(
                insert(parts_table),
                values
            )
            conn.commit()


if __name__ == '__main__':
    json_upload(args.file_path)
