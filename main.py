from fastapi import FastAPI, HTTPException, Depends, Request, Response, status, Query
from fastapi.middleware.cors import CORSMiddleware
import models
from database import SessionLocal, engine, get_db
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters
import sys
from routes import auth, biteship, blockchain, bulk_algorithm, items, marketplace, statistics, xendit, admin_settings, centra_finance, centra_setting, courier, wet_leaves, dry_leaves, flour, location, market_shipment, products, roles, shipment, subTransaction, transaction, users
from routes.public import pub_marketplace

sys.setrecursionlimit(10000)

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

cookie_params = CookieParameters(
    secure=False,  # Set to False for localhost development, True for production HTTPS
    httponly=True,
    samesite="lax"  # Use "lax" for localhost, "none" for cross-domain HTTPS
)

cookie = SessionCookie(
    cookie_name="session",
    identifier="general_verifier",
    auto_error=True,
    secret_key="DONOTUSE",
    cookie_params=cookie_params,
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",  # React default
        "http://localhost:5173",  # Vite default
        "http://localhost:5174",  # Vite alternative
        "http://localhost:8000", 
        "http://localhost:5004", 
        "https://leafty.csbihub.id", 
        "https://leafty-rest-api.csbihub.id",
        "https://leafty-mp.vercel.app"
    ],
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

@app.get("/")
def root():
    return

app.include_router(auth.router, tags=["Auth"])
app.include_router(users.router, tags=["Users"])
app.include_router(items.router, tags=["Items"])
app.include_router(xendit.router, tags=["Xendit"])
app.include_router(admin_settings.router, tags=["Admin Settings"])
app.include_router(biteship.router, tags=["Biteship"])
app.include_router(blockchain.router, tags=["Blockchain"])
app.include_router(centra_finance.router, tags=["Centra Finance"])
app.include_router(centra_setting.router, tags=["Centra Settings"])
app.include_router(courier.router, tags=["Courier"])
app.include_router(wet_leaves.router, tags=["Wet Leaves"])
app.include_router(dry_leaves.router, tags=["Dry Leaves"])
app.include_router(flour.router, tags=["Flour"])
app.include_router(location.router, tags=["Location"])
app.include_router(market_shipment.router, tags=["MarketShipment"])
app.include_router(products.router, tags=["Products"])
app.include_router(roles.router, tags=["Roles"])
app.include_router(shipment.router, tags=["Shipment"])
app.include_router(subTransaction.router, tags=["SubTransaction"])
app.include_router(transaction.router, tags=["Transaction"])
app.include_router(statistics.router, tags=["Statistics"])
app.include_router(marketplace.router, tags=["Marketplace"], dependencies=[Depends(cookie)])
app.include_router(pub_marketplace.router, tags=["Marketplace"])
app.include_router(bulk_algorithm.router, tags=["Bulk Algorithm"])


