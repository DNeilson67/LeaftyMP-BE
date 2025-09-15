from fastapi import APIRouter, HTTPException, Depends,  Response
from sqlalchemy.orm import Session
from BasicVerifier import BasicVerifier
from fastapi_sessions.backends.implementations import InMemoryBackend
from schemas.user_schemas import SessionData
from uuid import UUID, uuid4
import crud
from schemas.misc_schemas import LoginRequest
import bcrypt
from database import get_db
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
import bcrypt
import pyotp
from datetime import datetime, timedelta    
import smtplib
from dotenv import load_dotenv
import os

router = APIRouter()

backend = InMemoryBackend[UUID, SessionData]()

verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=True,
    backend=backend,
    auth_http_exception={"status": "404", "messages": "Session Not Found"}
)

cookie_params = CookieParameters(
    secure=True,  
    httponly=True,
    samesite="none" 
)


cookie = SessionCookie(
    cookie_name="session",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

@router.post("/login", tags=["Auth"])
async def login(request: LoginRequest, response: Response, db: Session = Depends(get_db)):
    user = crud.get_user_details_by_email(db, request.Email)
    
    if not user:
        raise HTTPException(404, "User does not exist.") # or raise HTTPException
    if not verify_password(request.Password, user.Password):  # Assuming user.Password is hashed
        raise HTTPException(401, "Invalid Credentials.")
    
    data = SessionData(UserID=user.UserID, Username = user.Username, RoleID=user.RoleID, Email=user.Email)

    SessionID = uuid4()
    
    await backend.create(SessionID, data)
    cookie.attach_to_response(response, SessionID)

    response.headers["Set-Cookie"] += "; SameSite=None"

    crud.create_session(db, SessionID, user.UserID)

    return {"code": "200", "status": "Login Successful"}

from schemas.user_schemas import User, UserCreate
@router.post('/register', response_model=User, tags=["Auth"])
def register(user: UserCreate, db: Session = Depends(get_db)):
    # Check if role exists, if not, return error
    role = crud.get_role(db, role_id=user.RoleID)
    if not role:
        raise HTTPException(status_code=400, detail="Role does not exist")

    # Create a new user
    return crud.create_user(db=db, user=user)


# Sessions
@router.post("/create_session/{user_id}")
async def create_session(user_id: str, response: Response, db: Session = Depends(get_db)):
    session = uuid4()
    user = crud.get_user_by_id(db, user_id)
    data = SessionData(user_id=user_id, user_role=user.RoleID, user_email=user.Email)

    await backend.create(session, data)
    cookie.attach_to_response(response, session)

    response.headers["Set-Cookie"] += "; SameSite=None"

    crud.create_session(db, session, user_id)

    return {"status": 200, "messages": "Session has been created successfully", "session_id": str(session)}


@router.get("/whoami", dependencies=[Depends(cookie)])
async def whoami(session_data: SessionData = Depends(verifier)):
    return session_data
    
@router.get('/get_location_user', dependencies=[Depends(cookie)])
async def get_location_user(db: Session = Depends(get_db), session_data: SessionData = Depends(verifier)):
    user_id = session_data.UserID
    location = crud.get_location_by_user_id(db, user_id)
    if not location:
        raise HTTPException(status_code=404, detail="Location not found")
    return location

@router.delete("/delete_session", dependencies=[Depends(cookie)])
async def del_session(response: Response, session_id: UUID = Depends(cookie), db: Session = Depends(get_db)):
   
    try:
        await backend.delete(session_id)
        cookie.delete_from_response(response)

        response.headers["Set-Cookie"] += "; SameSite=None"

        crud.delete_session(db)

        return {"status": 200, "messages": "Session has been deleted successfully"}
    except:
        return {"status": 404, "messages": "Session not found"}
    


# OTP
from schemas.otp_schemas import GenerateOTPRequest, OTPCreate, VerifyOTPRequest
@router.post("/generate_otp")
def generate_otp(request: GenerateOTPRequest, db: Session = Depends(get_db)):
    email = request.email
    
    secret = pyotp.random_base32()
    otp = pyotp.TOTP(secret)
    otp_code = otp.now()

    db_otp = crud.get_otp_by_email(db, email)    
    if db_otp:
        crud.delete_otp(db, email)

    hashed_otp_code = bcrypt.hashpw(otp_code.encode('utf-8'), bcrypt.gensalt())

    otp_create = OTPCreate(email=email, otp_code=hashed_otp_code, expires_at=datetime.now() + timedelta(minutes=2))
    crud.create_otp(db, otp_create)

    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()

    load_dotenv()
    USER_EMAIL = os.getenv("EMAIL")
    USER_PASSWORD = os.getenv("PASSWORD")
    
    server.login(USER_EMAIL, USER_PASSWORD)

    body = f"Your OTP is {otp_code}."
    subject = "OTP verification using python" 
    message = f'subject:{subject}\n\n{body}'

    server.sendmail(USER_EMAIL, email, message)
    server.quit()

    # print(f"OTP has been sent to {email}")
    # print(f"Generated OTP code for {email}: {otp_code}")

    return {"message": "OTP generated and sent to your email"}

# Endpoint to verify OTP
@router.post("/verify_otp")
def verify_otp(request: VerifyOTPRequest, db: Session = Depends(get_db)):
    email = request.email
    otp_code = request.otp_code

    db_otp = crud.get_otp_by_email(db, email)
    if not db_otp or not bcrypt.checkpw(otp_code.encode('utf-8'), db_otp.otp_code.encode('utf-8')) or db_otp.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    # OTP is valid, delete it from the database
    crud.delete_otp(db, email)
    
    return {"message": "OTP verified successfully"}