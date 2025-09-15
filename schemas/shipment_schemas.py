# Shipment and Courier schemas
from pydantic import BaseModel, UUID4
from typing import Optional, List
from datetime import datetime

class CourierBase(BaseModel):
    CourierName: str

class CourierCreate(CourierBase):
    pass

class Courier(CourierBase):
    CourierID: int
    class Config:
        orm_mode = True

class ShipmentBase(BaseModel):
    CourierID: int
    UserID: UUID4
    FlourIDs: List[int]
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
    FlourIDs: Optional[List[int]] = None
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
