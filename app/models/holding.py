from pydantic import BaseModel, Field
from datetime import datetime
from typing import Any,Optional

class NewHolding(BaseModel):
    asset_name: str
    quantity: int
    bought_price: float
    current_price: float
    date: datetime


class ResponseModel(BaseModel):
    success: bool
    message: str
    data: Any

class UpdateHolding(BaseModel):
    asset_name: Optional[str]
    quantity: Optional[int]
    bought_price: Optional[float]
    current_price: Optional[float]
    date: Optional[datetime]