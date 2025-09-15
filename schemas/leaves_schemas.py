# WetLeaves and DryLeaves schemas
from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime

class SimpleDryLeaves(BaseModel):
    id: int
    weight: float
    price: int
    discounted: bool
    initial_price: int

class DryLeavesBase(BaseModel):
    UserID: UUID4
    WetLeavesID: int
    Processed_Weight: Optional[float]
    Expiration: Optional[datetime]
    Status: Optional[str] = "Awaiting"

class DryLeavesCreate(DryLeavesBase):
    pass

class DryLeaves(DryLeavesBase):
    DryLeavesID: int
    class Config:
        orm_mode = True

class DryLeavesUpdate(BaseModel):
    Weight: float
    Expiration: Optional[datetime] = None

class DryLeavesStatusUpdate(BaseModel):
    Status: str

class WetLeavesBase(BaseModel):
    UserID: UUID4
    Weight: float
    ReceivedTime: datetime
    Expiration: datetime
    Status: Optional[str] = "Awaiting"

class WetLeavesCreate(WetLeavesBase):
    pass

class WetLeaves(WetLeavesBase):
    WetLeavesID: int
    class Config:
        orm_mode = True

class WetLeavesUpdate(BaseModel):
    Weight: float
    Expiration: Optional[datetime] = None

class WetLeavesStatusUpdate(BaseModel):
    Status: str
