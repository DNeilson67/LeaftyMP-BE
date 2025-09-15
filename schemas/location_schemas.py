# Location and City schemas
from pydantic import BaseModel, UUID4
from typing import Optional

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
    user: Optional['User']
