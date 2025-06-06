import json

from loguru import logger
import pandas as pd


DEALER_PRICE_LIST = 'data/prices/DEALER_PRICE_LIST.xlsb'
ELLIAS_PRICE_LIST = 'data/prices/Price Stock Elias Rus.xlsx'


def excel_to_json():
    logger.info('Начало предобработки данных их эксель файлов')
    try:
        mobis = pd.read_excel(DEALER_PRICE_LIST)
        ellias = pd.read_excel(ELLIAS_PRICE_LIST)

        mobis = mobis[
            [
                'PART_NO',
                'MODEL',
                'PART_NAME_ENG',
                'PART_NAME_RUS',
                'D_ORDER_DNP',
                'LIST_PRICE',
                'STOCK'
                ]
            ]
        ellias = ellias[['PART_NO', 'STOCK']]
        ellias.columns = ['PART_NO', 'STOCK_ELLIAS']

        price_all = pd.merge(
            mobis,
            ellias[['PART_NO', 'STOCK_ELLIAS']],
            on='PART_NO',
            how='left'
            )
        price_all['STOCK_ELLIAS'] = price_all[
            'STOCK_ELLIAS'
        ].fillna(0).astype('int64')

        parts_dict = dict(
            zip(
                price_all['PART_NO'],
                price_all[
                    [
                        'MODEL',
                        'PART_NAME_ENG',
                        'PART_NAME_RUS',
                        'D_ORDER_DNP',
                        'LIST_PRICE',
                        'STOCK',
                        'STOCK_ELLIAS'
                        ]
                    ].values.tolist()
                )
            )
        with open('data/merged_parts.json', 'w') as outfile:
            json.dump(parts_dict, outfile, ensure_ascii=False)
    except Exception as error:
        logger.error(
            f'Ошибка при предобработке данных: {error}'
            )
        return None


if __name__ == '__main__':
    excel_to_json()
