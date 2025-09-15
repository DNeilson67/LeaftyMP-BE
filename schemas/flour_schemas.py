# Flour schemas
from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SimpleFlour(BaseModel):
    id: int
    weight: float
    price: int
    discounted: bool
    initial_price: int

class FlourBase(BaseModel):
    UserID: str
    DryLeavesID: int
    Flour_Weight: float
    Expiration: Optional[datetime]
    Status: Optional[str] = "Awaiting"

class FlourCreate(FlourBase):
    pass

class Flour(FlourBase):
    FlourID: int
    class Config:
        orm_mode = True

class FlourUpdate(BaseModel):
    Weight: float
    Expiration: Optional[datetime] = None

class FlourStatusUpdate(BaseModel):
    Status: str
