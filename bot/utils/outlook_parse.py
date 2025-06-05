import asyncio
from datetime import date, datetime

from imap_tools import A, MailBox
from loguru import logger

from bot.config import settings


async def parse_price_data():
    try:
        async with MailBox(settings.IMAP_SERVER).login(
            settings.OUTLOOK_USERNAME,
            settings.OUTLOOK_PASSWORD
        ) as mailbox:
            today = datetime.today()
            mailbox.folder.set('INBOX')
            for msg in mailbox.fetch(
                A(
                    from_=settings.PARTS_EMAIL,
                    date=date(today.year, today.month, today.day)
                    )
                    ):
                for att in msg.attachments:
                    if 'xls' in str(att.filename):
                        with open(
                            'data/prices/{}'.format(att.filename), 'wb'
                        ) as file:
                            await file.write(att.payload)
    except asyncio.TimeoutError as error:
        logger.error(
            f'Ошибка при запросе: {error}'
            )
        return None
