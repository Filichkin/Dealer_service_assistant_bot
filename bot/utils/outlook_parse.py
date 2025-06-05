from datetime import date, datetime
from imap_tools import MailBox
from imap_tools import A

from bot.config import settings


today = datetime.today()

with MailBox(settings.IMAP_SERVER).login(
    settings.OUTLOOK_USERNAME,
    settings.OUTLOOK_PASSWORD
) as mailbox:
    mailbox.folder.set('INBOX')
    for msg in mailbox.fetch(
        A(
            from_='ynlebedev@kia.ru',
            date=date(today.year, today.month, today.day)
            )
            ):
        print(msg.date, msg.subject, len(msg.text or msg.html))
        for att in msg.attachments:
            if 'xls' in str(att.filename):
                print(att.filename, att.content_type)
                with open('data/prices/{}'.format(att.filename), 'wb') as f:
                    f.write(att.payload)
