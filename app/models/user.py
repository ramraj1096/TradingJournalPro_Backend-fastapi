from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import List, Optional

class User(BaseModel):
    name: str
    email: EmailStr
    password: str
    holdings: Optional[List[str]] = [] 
    trades: Optional[List[str]] = []  
    journal: Optional[List[str]] = []  
    created_at: datetime = Field(default_factory=datetime.now)
    is_banned: bool = False
    ban_time: Optional[datetime] = None

