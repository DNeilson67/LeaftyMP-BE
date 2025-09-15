from pydantic import BaseModel, UUID4
from typing import Optional
from datetime import datetime


class trx_form(BaseModel):
    userId: UUID4
    trx_id: str

class BlockchainTrxCreate(BaseModel):
    trx_id: str

class BlockchainTrxBase(BaseModel):
    UserID: str
    TrxId: str
    CreatedAt: Optional[datetime] = None

class BlockchainTrxResponse(BlockchainTrxBase):
    username: Optional[str] = None
    user_email: Optional[str] = None

    class Config:
        orm_mode = True

class BlockchainTrxListResponse(BaseModel):
    message: str
    data: list[BlockchainTrxResponse]

class BlockchainTrxSingleResponse(BaseModel):
    message: str
    data: BlockchainTrxResponse