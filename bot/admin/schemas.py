from pydantic import BaseModel, Field


class ServiceIDModel(BaseModel):
    id: int


class ServiceModel(BaseModel):
    name: str = Field(..., min_length=5)
    description: str = Field(..., min_length=5)
    price: int = Field(..., gt=0)
    hidden_content: str = Field(..., min_length=5)
