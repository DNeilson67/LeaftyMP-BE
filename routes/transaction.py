from typing import Dict, List, Union
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
from schemas.transaction_schemas import Transaction, TransactionCreate, TransactionUpdate

router = APIRouter()

@router.post("/transaction/post", response_model=Transaction, tags=["Transaction"])
def create_transaction(transaction: TransactionCreate, db: Session = Depends(get_db)):
    return crud.create_transaction(db=db, transaction=transaction)

@router.get("/transactions/get", response_model=List[Transaction], tags=["Transaction"])
def get_transactions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_transactions(db=db, skip=skip, limit=limit)

@router.get("/transaction/get/{transaction_id}", response_model=Transaction, tags=["Transaction"])
def get_transaction(transaction_id: str, db: Session = Depends(get_db)):
    transaction = crud.get_transaction_by_id(db=db, transaction_id=transaction_id)
    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return transaction

@router.put("/transaction/put/{transaction_id}", response_model=Transaction, tags=["Transaction"])
def update_transaction(transaction_id: str, transaction_update: TransactionUpdate, db: Session = Depends(get_db)):
    updated_transaction = crud.update_transaction(db=db, transaction_id=str(transaction_id), transaction_update=transaction_update)
    if not updated_transaction:
        raise HTTPException(status_code=404, detail="Transaction not found")
    return updated_transaction

@router.delete("/transaction/delete/{transaction_id}", response_class=JSONResponse, tags=["Transaction"])
def delete_transaction(transaction_id: str, db: Session = Depends(get_db)):
    deleted = crud.delete_transaction(db, transaction_id)
    if deleted:
        return {"message": "Transaction deleted successfully"}
    else:
        return {"message": "Transaction not found or deletion failed"}