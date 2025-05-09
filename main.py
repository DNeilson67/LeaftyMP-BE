from fastapi import FastAPI, HTTPException, Depends, Request, Response, status, Query
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from typing import List
import uvicorn
import uuid
from BasicVerifier import BasicVerifier
from fastapi_sessions.backends.implementations import InMemoryBackend
from schemas import User, SessionData
from uuid import UUID, uuid4
from fastapi.middleware.cors import CORSMiddleware
import crud
import requests
import base64
import models
import schemas
from schemas import InvoiceRequest
import bcrypt
from typing import List, Union, Dict
from database import SessionLocal, engine, get_db
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
from fastapi_sessions.session_verifier import SessionVerifier
import sys
from routes import items, statistics, xendit,admin_setting,centra_finance,centra_setting,courier,dry_leaves,flour,location,market_shipment,products,roles,shipment,subTransaction,transaction,users,wet_leaves
import bcrypt
import pyotp
from datetime import datetime, timedelta    
import smtplib
from dotenv import load_dotenv
import os


sys.setrecursionlimit(10000)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

backend = InMemoryBackend[UUID, SessionData]()

verifier = BasicVerifier(
    identifier="general_verifier",
    auto_error=False,
    backend=backend,
    auth_http_exception={"status": "404", "messages": "Session Not Found"}
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:8000", "https://leafty-be.vercel.app", "https://leafty.vercel.app", "https://leafty.portproject.my.id", "http://leafty-rest-api.portproject.my.id"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def db_session_middleware(request: Request, call_next):
    response = Response("Internal server error", status_code=500)
    try:
        request.state.db = SessionLocal()
        response = await call_next(request)
    finally:
        request.state.db.close()
    return response

cookie_params = CookieParameters(
    secure=True,  # Ensures cookie is sent over HTTPS
    httponly=True,
    samesite="none"  # Allows the cookie to be sent with cross-origin requests
)

cookie = SessionCookie(
    cookie_name="session",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)

@app.get("/")
def root():
    return

def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

@app.post("/login", tags=["Auth"])
async def login(request: schemas.LoginRequest, response: Response, db: Session = Depends(get_db)):
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

@app.post('/register', response_model=schemas.User, tags=["Auth"])
def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    # Check if role exists, if not, return error
    role = crud.get_role(db, role_id=user.RoleID)
    if not role:
        raise HTTPException(status_code=400, detail="Role does not exist")

    # Create a new user
    return crud.create_user(db=db, user=user)

# def format_large_number(number):
#     if number < 1000:
#         return str(number)
#     elif number < 1_000_000:
#         return f"{number // 1000},{number % 1000}k"
#     else:
#         return f"{number // 1_000_000},{(number // 1000) % 1000}m"


app.include_router(items.router, tags=["Items"])
app.include_router(xendit.router, tags=["Xendit"])
app.include_router(admin_setting.router, tags=["Admin Settings"])
app.include_router(centra_finance.router, tags=["Centra Finance"])
app.include_router(centra_setting.router, tags=["Centra Settings"])
app.include_router(courier.router, tags=["Courier"])
app.include_router(dry_leaves.router, tags=["Dry Leaves"])
app.include_router(flour.router, tags=["Flour"])
app.include_router(location.router, tags=["Location"])
app.include_router(market_shipment.router, tags=["MarketShipment"])
app.include_router(products.router, tags=["Products"])
app.include_router(roles.router, tags=["Roles"])
app.include_router(shipment.router, tags=["Shipment"])
app.include_router(subTransaction.router, tags=["SubTransaction"])
app.include_router(transaction.router, tags=["Transaction"])
app.include_router(users.router, tags=["Users"])
app.include_router(wet_leaves.router, tags=["Wet Leaves"])
app.include_router(statistics.router, tags=["Wet Leaves"])



@app.get("/algorithm/bulkCentra", response_model=Dict[str, Union[int, Dict[str, List[Union[schemas.SimpleFlour, schemas.SimpleDryLeaves]]]]], tags=["Algorithm"])
def bulk_item_selection_by_random_centras(item_type: str, target_weight: int, db: Session = Depends(get_db)):
    try:
        max_value, choices = crud.bulk_algorithm_by_random_centras(db, item_type=item_type, target_weight=target_weight)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"max_value": max_value, "choices": choices}


@app.post("/algorithm/bulkSelectedCentra", response_model=Dict[str, Union[int, Dict[str, List[Union[schemas.SimpleFlour, schemas.SimpleDryLeaves]]]]], tags=["Algorithm"])
def bulk_item_selection_by_selected_centras(request: schemas.BulkItemSelectionRequest, db: Session = Depends(get_db)):
    try:
        max_value, choices = crud.bulk_algorithm_by_selected_centra(
            db, 
            item_type=request.item_type, 
            target_weight=request.target_weight, 
            users=request.users
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"max_value": max_value, "choices": choices}


# @app.get("/algorithm/bulkClosestCentra", response_model=Dict[str, Union[int, Dict[str, List[Union[schemas.SimpleFlour, schemas.SimpleDryLeaves]]]]], tags=["Algorithm"])
# def bulk_item_selection_by_centras(item_type: str, target_weight: int, db: Session = Depends(get_db)):
#     try:
#         max_value, choices = crud.bulk_algorithm_by_random_centras(db, item_type=item_type, target_weight=target_weight)
#     except ValueError as e:
#         raise HTTPException(status_code=400, detail=str(e))
    
#     return {"max_value": max_value, "choices": choices}




@app.get("/algorithm/bulkItem", response_model=Dict[str, Union[int, Dict[str, List[Union[schemas.SimpleFlour, schemas.SimpleDryLeaves]]]]], tags=["Algorithm"])
def bulk_item_selection_by_items(item_type: str, target_weight: int, db: Session = Depends(get_db)):
    try:
        max_value, choices = crud.bulk_algorithm_by_random_items(db, item_type=item_type, target_weight=target_weight)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"max_value": max_value, "choices": choices}

    
# Sessions
@app.post("/create_session/{user_id}", tags=["Sessions"])
async def create_session(user_id: str, response: Response, db: Session = Depends(get_db)):
    session = uuid4()
    user = crud.get_user_by_id(db, user_id)
    data = SessionData(user_id=user_id, user_role=user.RoleID, user_email=user.Email)

    await backend.create(session, data)
    cookie.attach_to_response(response, session)

    response.headers["Set-Cookie"] += "; SameSite=None"

    crud.create_session(db, session, user_id)

    return f"created session for {user_id}"


@app.get("/whoami", dependencies=[Depends(cookie)], tags=["Sessions"])
async def whoami(session_data: SessionData = Depends(verifier)):
    return session_data
    
    

@app.delete("/delete_session", dependencies=[Depends(cookie)], tags=["Sessions"])
async def del_session(response: Response, session_id: UUID = Depends(cookie), db: Session = Depends(get_db)):
   
    try:
        await backend.delete(session_id)
        cookie.delete_from_response(response)

        response.headers["Set-Cookie"] += "; SameSite=None"

        crud.delete_session(db)

        return {"status": "200", "messages": "Session has been deleted successfully"}
    except:
        return {"status": "404", "messages": "Session not found"}
    


# OTP
@app.post("/generate_otp", tags=["OTP"])
def generate_otp(request: schemas.GenerateOTPRequest, db: Session = Depends(get_db)):
    email = request.email
    
    secret = pyotp.random_base32()
    otp = pyotp.TOTP(secret)
    otp_code = otp.now()

    db_otp = crud.get_otp_by_email(db, email)    
    if db_otp:
        crud.delete_otp(db, email)

    hashed_otp_code = bcrypt.hashpw(otp_code.encode('utf-8'), bcrypt.gensalt())

    otp_create = schemas.OTPCreate(email=email, otp_code=hashed_otp_code, expires_at=datetime.now() + timedelta(minutes=2))
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

    print(f"OTP has been sent to {email}")
    print(f"Generated OTP code for {email}: {otp_code}")

    return {"message": "OTP generated and sent to your email"}

# Endpoint to verify OTP
@app.post("/verify_otp", tags=["OTP"])
def verify_otp(request: schemas.VerifyOTPRequest, db: Session = Depends(get_db)):
    email = request.email
    otp_code = request.otp_code

    db_otp = crud.get_otp_by_email(db, email)
    if not db_otp or not bcrypt.checkpw(otp_code.encode('utf-8'), db_otp.otp_code.encode('utf-8')) or db_otp.expires_at < datetime.now():
        raise HTTPException(status_code=400, detail="Invalid or expired OTP")
    
    # OTP is valid, delete it from the database
    crud.delete_otp(db, email)
    
    return {"message": "OTP verified successfully"}