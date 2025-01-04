from pydantic import BaseModel
from datetime import datetime
from typing import Any

class NewTrade(BaseModel):
    asset_name: str
    quantity: int
    trade_type: str
    asset_type: str
    trade_category: str
    enter_price: float
    exit_price: float
    strategy_name: str
    strategy_description: str
    date: datetime



class ResponseModel(BaseModel):
    success: bool
    message: str
    data: Any

