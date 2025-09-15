# Miscellaneous schemas
from pydantic import BaseModel, UUID4, EmailStr
from typing import List

class BulkItemSelectionRequest(BaseModel):
    item_type: str
    target_weight: int
    users: List[UUID4]

class LoginRequest(BaseModel):
    Email: EmailStr
    Password: str

class MarketPlaceFindItem(BaseModel):
    product_id: int
    product_name: str
    username: str
