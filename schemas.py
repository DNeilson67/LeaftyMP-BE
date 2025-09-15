from pydantic import BaseModel, UUID4, EmailStr, RootModel, Field
from typing import Optional, List, Dict

from datetime import datetime

class GenerateOTPRequest(BaseModel):
    email: str

# Model for verifying OTP request
class VerifyOTPRequest(BaseModel):
    email: str
    otp_code: str
    
class RoleBase(BaseModel):
    RoleName: str
    
class SessionData(BaseModel):
    UserID: str
    Username: str
    RoleID: int
    Email: str

class OTPBase(BaseModel):
    email: str
    otp_code: str
    expires_at: datetime

class OTPCreate(OTPBase):
    pass

class OTP(OTPBase):
    class Config:
        orm_mode = True

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    RoleID: int

    class Config:
        orm_mode = True

class UserBase(BaseModel):
    Username: str
    Email: str
    PhoneNumber: Optional[int]
    RoleID: int
    Password: str
    
class UserResponse(BaseModel):
    UserID: UUID4
    Username: str
    Email: str
    RoleID: int

class UserCreate(UserBase):
    location_address: str
    longitude: float
    latitude: float
    
class UserRoleUpdate(BaseModel):
    RoleName: str
  
class UserPhoneUpdate(BaseModel):
    PhoneNumber: int

class UserUpdate(BaseModel):
    Password: Optional[str] = None
    Username: Optional[str] = None
    Email: Optional[str] = None
    
class AdminUserUpdate(BaseModel):
    Username: Optional[str] 
    Email: Optional[str] 
    PhoneNumber: Optional[int] 
    RoleName: Optional[str] 

class User(UserBase):
    UserID: UUID4
    role: Role

    class Config:
        orm_mode = True

class LocationBase(BaseModel):
    user_id: str
    location_address: str
    latitude: float
    longitude: float

class LocationCreate(LocationBase):
    pass


class LocationPatch(BaseModel):
    location_address: str
    latitude: float
    longitude: float

class Location(LocationBase):
    user_id: str

    class Config:
        orm_mode = True

class CourierBase(BaseModel):
    CourierName: str

class CourierCreate(CourierBase):
    pass

class Courier(CourierBase):
    CourierID: int

    class Config:
        orm_mode = True

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

class ShipmentBase(BaseModel):
    CourierID: int
    UserID: UUID4
    FlourIDs: List[int]  # Modified to accept a list of Flour IDs
    ShipmentQuantity: int
    ShipmentDate: Optional[datetime] = None 
    Check_in_Date: Optional[datetime]= None
    Check_in_Quantity: Optional[int]= None
    Harbor_Reception_File: Optional[bool]= None
    Rescalled_Weight: Optional[float]= None
    Rescalled_Date: Optional[datetime]= None
    Centra_Reception_File: Optional[bool]= None

class ShipmentCreate(ShipmentBase):
    pass

class ShipmentUpdate(BaseModel):
    CourierID: Optional[int] = None
    FlourIDs: Optional[List[int]] = None  # Modified to accept a list of Flour IDs
    ShipmentQuantity: Optional[int] = None
    Check_in_Quantity: Optional[int] = None
    Harbor_Reception_File: Optional[str] = None
    Rescalled_Weight: Optional[float] = None
    Centra_Reception_File: Optional[str] = None
    
class Shipment(ShipmentBase):
    ShipmentID: int

class ShipmentDateUpdate(BaseModel):
    ShipmentDate: Optional[datetime] = None

class ShipmentCheckInUpdate(BaseModel):
    Check_in_Date: Optional[datetime] = None
    Check_in_Quantity: Optional[int] = None
    
class ShipmentRescalledWeightUpdate(BaseModel):
    Rescalled_Weight: Optional[float] = None
    Rescalled_Date: Optional[datetime] = None

class ShipmentHarborReceptionUpdate(BaseModel):
    Harbor_Reception_File: Optional[bool] = None

class ShipmentCentraReceptionUpdate(BaseModel):
    Centra_Reception_File: Optional[bool] = None
    
class ShipmentFlourAssociationBase(BaseModel):
    shipment_id: int
    flour_id: int

class ShipmentFlourAssociationCreate(ShipmentFlourAssociationBase):
    pass

class ShipmentFlourAssociation(ShipmentFlourAssociationBase):

    class Config:
        orm_mode = True
        
        
# marketplace stuff

# Base model for AdminSettings
class AdminSettingsBase(BaseModel):
    AdminFeeValue: float

class AdminSettingsCreate(AdminSettingsBase):
    pass

class AdminSettings(AdminSettingsBase):
    AdminSettingsID: int

    class Config:
        orm_mode = True



# Base model for Products
class ProductsBase(BaseModel):
    ProductName: str

class ProductsCreate(ProductsBase):
    pass

class Products(ProductsBase):
    ProductID: int

    class Config:
        orm_mode = True

# Base model for Centrabasesettings
class CentraBaseSettingsBase(BaseModel):
    UserID: UUID4
    ProductID: int
    InitialPrice: float
    Sellable: bool  

class CentraBaseSettingsCreate(CentraBaseSettingsBase):
    pass

class CentraBaseSettings(CentraBaseSettingsBase):
    SettingsID: int
    products: Optional[Products]  

    class Config:
        orm_mode = True
        
class CentraBaseSettingUpdate(BaseModel):
    InitialPrice: float
    Sellable: bool


# Base model for CentraSettingDetail
class CentraSettingDetailBase(BaseModel):
    UserID: str  # Updated from UUID4 to str to match VARCHAR column type
    ProductID: int
    DiscountRate: int
    ExpDayLeft: int

class CentraSettingDetailCreate(CentraSettingDetailBase):
    pass

class CentraSettingDetail(CentraSettingDetailBase):
    SettingDetailID: int
    products_templates: Optional["Products"]  # Updated to match relationship name in ORM model

    class Config:
        orm_mode = True

class CentraSettingDetailUpdate(BaseModel):
    DiscountRate: Optional[float] = None
    ExpDayLeft: Optional[int] = None
# --- MarketShipment Schemas ---

class MarketShipmentBase(BaseModel):
    CentraID: str  # Still used to assign product to a Centra
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


# --- SubTransaction Schemas ---
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


# --- Transaction Schemas ---
class TransactionCreate(BaseModel):
    CustomerID: UUID4  # ✅ Added as required input
    TransactionStatus: Optional[str] = "pending"
    sub_transactions: List[SubTransactionCreate]  # Can create with children

class TransactionUpdate(BaseModel):
    TransactionStatus: Optional[str] = None
    sub_transactions: Optional[List[SubTransactionUpdate]] = None

class Transaction(BaseModel):
    TransactionID: UUID4
    CustomerID: UUID4
    TransactionStatus: str
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
    ProductName: str  # The name of the product (like "Powder")

    class Config:
        orm_mode = True

class SubTransactionDisplayBase(BaseModel):
    SubTransactionStatus: str
    CentraUsername: str
    market_shipments: List[MarketShipmentDisplayBase]

    class Config:
        orm_mode = True

class TransactionDisplayBase(BaseModel):
    TransactionID: str  # UUID as a string
    TransactionStatus: str
    CreatedAt: Optional[datetime]  # Optional datetime field for creation
    ExpirationAt: Optional[datetime]  # Optional datetime field for expiration
    sub_transactions: List[SubTransactionDisplayBase]

    class Config:
        orm_mode = True

        
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


#xendit
class InvoiceRequest(BaseModel):
    external_id: str
    amount: int
    payer_email: str
    description: str
    success_redirect_url: str
    failure_redirect_url: str
    
#xendit
class XenditInvoiceRequestBody(BaseModel):
    id: str
    external_id: str
    user_id: str
    is_high: bool
    payment_method: str
    status: str
    merchant_name: str
    amount: float
    paid_amount: float
    bank_code: str
    paid_at: datetime
    payer_email: EmailStr
    description: Optional[str] = "No description"
    adjusted_received_amount: Optional[float] = 0.0
    fees_paid_amount: Optional[float] = 0.0
    updated: datetime
    created: datetime
    currency: str
    payment_channel: str
    payment_destination: str
    
class InvoicePaidWebhook(BaseModel):
    id: str
    external_id: str
    user_id: str
    is_high: bool
    payment_method: str
    status: str
    merchant_name: str
    amount: float
    paid_amount: float
    bank_code: str
    paid_at: datetime
    payer_email: EmailStr
    description: Optional[str] = "No description"
    adjusted_received_amount: Optional[float] = 0.0
    fees_paid_amount: Optional[float] = 0.0
    updated: datetime
    created: datetime
    currency: str
    payment_channel: str
    payment_destination: str
    payment_id: str
    failure_redirect_url: Optional[str] = None
    success_redirect_url: Optional[str] = None

class CityBase(BaseModel):
    user_id: str
    name: str
    lat: Optional[float]
    lng: Optional[float]

    class Config:
        orm_mode = True 

class CityCreate(CityBase):
    pass  


class City(CityBase):
    user: Optional[User] 
    
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

#biteship
class Coordinates(BaseModel):
    latitude: float
    longitude: float

class Item(BaseModel):
    name: str
    description: str
    category: str
    value: int
    quantity: int
    height: int
    length: int
    weight: int
    width: int

class ShipmentData(BaseModel):
    shipper_contact_name: str
    shipper_contact_phone: str
    shipper_contact_email: str
    shipper_organization: str
    origin_contact_name: str
    origin_contact_phone: str
    origin_address: str
    origin_note: str
    origin_coordinate: Coordinates
    destination_contact_name: str
    destination_contact_phone: str
    destination_contact_email: str
    destination_address: str
    destination_note: str
    destination_coordinate: Coordinates
    courier_company: str
    courier_type: str
    courier_insurance: int
    delivery_type: str
    order_note: str
    metadata: Dict = Field(default_factory=dict)
    items: List[Item]


class trx_form(BaseModel):
    userId: UUID4
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