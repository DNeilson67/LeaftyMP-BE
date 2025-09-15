# place, AdminSettings, Products, CentraBaseSettings schemas
from pydantic import BaseModel, UUID4
from typing import Optional

class AdminSettingsBase(BaseModel):
    AdminFeeValue: float

class AdminSettingsCreate(AdminSettingsBase):
    pass

class AdminSettings(AdminSettingsBase):
    AdminSettingsID: int
    class Config:
        orm_mode = True

class ProductsBase(BaseModel):
    ProductName: str

class ProductsCreate(ProductsBase):
    pass

class Products(ProductsBase):
    ProductID: int
    class Config:
        orm_mode = True

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

class CentraSettingDetailBase(BaseModel):
    UserID: str
    ProductID: int
    DiscountRate: int
    ExpDayLeft: int

class CentraSettingDetailCreate(CentraSettingDetailBase):
    pass

class CentraSettingDetail(CentraSettingDetailBase):
    SettingDetailID: int
    products_templates: Optional[Products]
    class Config:
        orm_mode = True

class CentraSettingDetailUpdate(BaseModel):
    DiscountRate: Optional[float] = None
    ExpDayLeft: Optional[int] = None
