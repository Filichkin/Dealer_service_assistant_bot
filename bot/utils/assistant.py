from loguru import logger
from mistralai import Mistral

from bot.config import settings


def assistant_service(prompt: str):
    logger.info('Подготовка ответа от ассистента.')
    try:
        client = Mistral(api_key=settings.MISTRAL_TOKEN)
        signed_url = client.files.get_signed_url(
            file_id=settings.MISTRAL_FILE_ID
            )
        print(signed_url.url)
        system = """
                    Ты — внутренний менеджер отдела гарантии Киа.
                    Отвечаешь по делу без лишних вступлений.
                    """

        messages = [
            {'role': 'system', 'content': system},
            {
                'role': 'user',
                'content': [
                    {
                        'type': 'text',
                        'text': prompt
                    },
                    {
                        'type': 'document_url',
                        'document_url': signed_url.url
                    }
                ]
            }
        ]
        chat_response = client.chat.complete(
            model=settings.MISTRAL_MODEL,
            messages=messages
        )
        return chat_response.choices[0].message.content
    except Exception as error:
        logger.error(
            f'Ошибка при подготовке ответа: {error}'
            )
        return 'Ошибка при подготовке ответа'
