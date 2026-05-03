# Transaction and SubTransaction schemas
from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime

class MarketShipmentBase(BaseModel):
    CentraID: str
    ProductTypeID: int
    ProductID: int
    Price: float
    InitialPrice: float
    ShipmentStatus: Optional[str] = None

class MarketShipmentCreate(MarketShipmentBase):
    pass

class MarketShipmentUpdate(BaseModel):
    CentraID: Optional[UUID4] = None
    ProductTypeID: Optional[int] = None
    ProductID: Optional[int] = None
    Price: Optional[float] = None
    InitialPrice: Optional[float] = None
    ShipmentStatus: Optional[str] = None

class MarketShipment(MarketShipmentBase):
    MarketShipmentID: int
    class Config:
        orm_mode = True

class MarketShipmentWithCentra(BaseModel):
    """MarketShipment response model that includes CentraID from SubTransaction"""
    MarketShipmentID: int
    CentraID: str
    ProductTypeID: int
    ProductID: int
    Price: float
    InitialPrice: float
    ShipmentStatus: Optional[str] = None

class SubTransactionBase(BaseModel):
    SubTransactionStatus: str

class SubTransactionCreate(SubTransactionBase):
    market_shipments: List[MarketShipmentCreate]

class SubTransactionUpdate(BaseModel):
    SubTransactionStatus: Optional[str] = None
    market_shipments: Optional[List[MarketShipmentUpdate]] = None

class SubTransaction(SubTransactionBase):
    SubTransactionID: int
    market_shipments: List[MarketShipment]
    class Config:
        orm_mode = True

class TransactionCreate(BaseModel):
    CustomerID: UUID4
    sub_transactions: List[SubTransactionCreate]
    # Optional shipping address - if not provided, will use user's default location
    ShippingLatitude: Optional[float] = None
    ShippingLongitude: Optional[float] = None
    ShippingAddress: Optional[str] = None

class TransactionUpdate(BaseModel):
    TransactionStatus: Optional[str] = None
    sub_transactions: Optional[List[SubTransactionUpdate]] = None
    ShippingLatitude: Optional[float] = None
    ShippingLongitude: Optional[float] = None
    ShippingAddress: Optional[str] = None

class Transaction(BaseModel):
    TransactionID: UUID4
    CustomerID: UUID4
    TransactionStatus: str
    ShippingLatitude: Optional[float] = None
    ShippingLongitude: Optional[float] = None
    ShippingAddress: Optional[str] = None
    CreatedAt: datetime
    sub_transactions: List[SubTransaction]
    class Config:
        orm_mode = True

class MarketShipmentDisplayBase(BaseModel):
    ProductID: int
    InitialPrice: float
    Price: float
    ShipmentStatus: str
    Weight: float
    ProductName: str
    class Config:
        orm_mode = True

class SubTransactionDisplayBase(BaseModel):
    SubTransactionStatus: str
    CentraUsername: str
    market_shipments: List[MarketShipmentDisplayBase]
    class Config:
        orm_mode = True

class TransactionDisplayBase(BaseModel):
    TransactionID: str
    TransactionStatus: str
    ShippingLatitude: Optional[float] = None
    ShippingLongitude: Optional[float] = None
    ShippingAddress: Optional[str] = None
    CreatedAt: Optional[datetime]
    ExpirationAt: Optional[datetime]
    sub_transactions: List[SubTransactionDisplayBase]
    class Config:
        orm_mode = True

# Shipping Address Update Schema
class ShippingAddressUpdate(BaseModel):
    ShippingLatitude: float
    ShippingLongitude: float
    ShippingAddress: str

# Bulk Transaction Schemas
class BulkMarketShipmentItem(BaseModel):
    """Individual item in a bulk transaction"""
    CentraID: str
    ProductTypeID: int
    ProductID: int
    Price: float
    InitialPrice: float
    Weight: float
    # Removed ProductName - not needed for backend

class BulkTransactionCreate(BaseModel):
    """Schema for creating bulk transactions with multiple items"""
    items: List[BulkMarketShipmentItem]
    # Removed TransactionStatus - will default to "Transaction Pending"

class BulkTransactionResponse(BaseModel):
    """Response schema for bulk transaction creation"""
    TransactionID: str
    message: str
    total_items: int
    failed_items: Optional[List[dict]] = None



