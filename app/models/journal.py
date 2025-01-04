from pydantic import BaseModel, Field
from datetime import datetime
from typing import List, Optional,Any

class NewJournal(BaseModel):
    asset_name: str
    quantity: int
    asset_type: str
    journal_for: str
    trade_category: str
    enter_price: float
    exit_price: float
    stop_loss: float
    strategy_name: str
    strategy_description: str
    date: datetime



class UpdateJournal(BaseModel):
    asset_name: Optional[str]
    quantity: Optional[int]
    asset_type: Optional[str]
    journal_for: Optional[str]
    trade_category: Optional[str]
    enter_price: Optional[float]
    exit_price: Optional[float]
    stop_loss: Optional[float]
    strategy_name: Optional[str]
    strategy_description: Optional[str]
    date: Optional[datetime]


class ResponseModel(BaseModel):
    success: bool
    message: str
    data: Any