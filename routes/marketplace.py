from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException, Query
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
from schemas.transaction_schemas import MarketShipmentCreate
from schemas.transaction_schemas import TransactionDisplayBase
from schemas.user_schemas import SessionData
from routes.auth import verifier

router = APIRouter()

@router.post("/marketplace/create_transaction")                
def create_new_transaction(market_shipment: MarketShipmentCreate, db: Session = Depends(get_db), session_data: SessionData = Depends(verifier)):
    return crud.create_single_transaction_by_customer(db=db, market_shipment=market_shipment, session_data=session_data)                     

@router.get("/marketplace/get_transactions_by_customer", response_model=List[TransactionDisplayBase])
def get_marketplace_transaction_details(
    session_data: SessionData = Depends(verifier),
    db: Session = Depends(get_db)
):
    transaction = crud.get_transactions_by_customer(db=db, session_data=session_data)
    
    return transaction

@router.get("/marketplace/get_transaction_details/{transaction_id}", response_model=TransactionDisplayBase)
def get_marketplace_transaction_details(
    transaction_id: str,
    session_data: SessionData = Depends(verifier),
    db: Session = Depends(get_db)
):
    transaction = crud.get_transaction_details_by_id(db=db, transaction_id=transaction_id, session_data=session_data)
    
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    
    return transaction