# User, Role, Session schemas
from pydantic import BaseModel, UUID4, EmailStr
from typing import Optional

class RoleBase(BaseModel):
    RoleName: str

class RoleCreate(RoleBase):
    pass

class Role(RoleBase):
    RoleID: int
    class Config:
        orm_mode = True

class SessionData(BaseModel):
    UserID: str
    Username: str
    RoleID: int
    Email: str

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
