from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class TelegramIDModel(BaseModel):
    telegram_id: int

    model_config = ConfigDict(from_attributes=True)


class UserModel(TelegramIDModel):
    username: str | None
    first_name: str | None
    last_name: str | None


class ServiceIDModel(BaseModel):
    id: int


class PaymentData(BaseModel):
    user_id: int = Field(..., description='ID пользователя Telegram')
    payment_id: str = Field(
        ...,
        max_length=255,
        description='Уникальный ID платежа'
        )
    price: int = Field(..., description='Сумма платежа в рублях')
    service_id: int = Field(..., description='ID товара')
    expire: datetime
