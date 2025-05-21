from pydantic import BaseModel, Field


class PaymentIDModel(BaseModel):
    id: int


class PaymentModel(BaseModel):
    price: int = Field(..., gt=0)
    user_id: int = Field(..., gt=0)
