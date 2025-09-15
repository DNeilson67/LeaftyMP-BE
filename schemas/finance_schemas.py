# CentraFinance schemas
from pydantic import BaseModel, UUID4

class CentraFinanceBase(BaseModel):
    UserID: UUID4
    AccountHolderName: str
    BankCode: str
    BankAccountNumber: str

class CentraFinanceCreate(CentraFinanceBase):
    pass

class CentraFinance(CentraFinanceBase):
    FinanceID: int
    class Config:
        orm_mode = True
