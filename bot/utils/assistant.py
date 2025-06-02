from mistralai import Mistral

from bot.config import settings


model = settings.MISTRAL_MODEL

client = Mistral(api_key=settings.MISTRAL_TOKEN)

uploaded_pdf = client.files.upload(
    file={
        'file_name': 'warranty_policy.pdf',
        'content': open('data/warranty_policy.pdf', 'rb'),
         },
    purpose='ocr'
)
signed_url = client.files.get_signed_url(file_id=uploaded_pdf.id)

messages = [
    {
        'role': 'user',
        'content': [
            {
                'type': 'text',
                'text': 'Как подать гарантийное с типом D'
            },
            {
                'type': 'document_url',
                # "document_url": "https://arxiv.org/pdf/1805.04770"
                'document_url': signed_url.url
            }
        ]
    }
]

# Get the chat response
chat_response = client.chat.complete(
    model=model,
    messages=messages
)

print(chat_response.choices[0].message.content)
