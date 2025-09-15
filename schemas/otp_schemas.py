# OTP related schemas
from pydantic import BaseModel
from datetime import datetime

class GenerateOTPRequest(BaseModel):
    email: str

class VerifyOTPRequest(BaseModel):
    email: str
    otp_code: str

class OTPBase(BaseModel):
    email: str
    otp_code: str
    expires_at: datetime

class OTPCreate(OTPBase):
    pass

class OTP(OTPBase):
    class Config:
        orm_mode = True
