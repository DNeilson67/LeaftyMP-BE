from typing import Dict, List, Union
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
from schemas.transaction_schemas import Transaction, TransactionCreate, TransactionUpdate, ShippingAddressUpdate, BulkMarketShipmentItem
import schemas
from .auth import verifier, cookie
from pydantic import BaseModel

router = APIRouter()

# Schema for transaction calculation request
class TransactionCalculationRequest(BaseModel):
    items: List[BulkMarketShipmentItem]
    
class TransactionCalculationResponse(BaseModel):
    subtotal: float
    admin_fee: float
    shipping_fee: float
    total_amount: float
    total_weight: float

@router.post("/transaction/calculate", response_model=TransactionCalculationResponse, tags=["Transaction"])
def calculate_transaction_totals(request: TransactionCalculationRequest, db: Session = Depends(get_db)):
    """Calculate transaction totals including admin fee and shipping fee"""
    try:
        # Calculate subtotal from items
        subtotal = sum(item.Weight * item.Price for item in request.items)
        
        # Calculate total weight
        total_weight = sum(item.Weight for item in request.items)
        
        # Get admin fee from database
        admin_settings = crud.get_admin_settings(db=db)
        admin_fee = admin_settings.AdminFeeValue if admin_settings else 5000.0
        
        # Calculate shipping fee based on total weight (dummy calculation)
        # You can adjust this formula based on your business logic
        # For now: Rp 10,000 base + Rp 1,000 per kg
        base_shipping = 10000.0
        per_kg_rate = 1000.0
        shipping_fee = base_shipping + (total_weight * per_kg_rate)
        
        # Calculate total
        total_amount = subtotal + admin_fee + shipping_fee
        
        return TransactionCalculationResponse(
            subtotal=subtotal,
            admin_fee=admin_fee,
            shipping_fee=shipping_fee,
            total_amount=total_amount,
            total_weight=total_weight
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error calculating transaction: {str(e)}")

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

# Row-level locking transaction endpoints
@router.put("/transaction/{transaction_id}/complete", response_class=JSONResponse, tags=["Transaction"])
def complete_transaction(transaction_id: str, user_id: str, db: Session = Depends(get_db)):
    """Complete a transaction and update products to 'Processed' status with row-level locking"""
    try:
        result = crud.complete_transaction_and_process_product(
            db=db, 
            transaction_id=transaction_id, 
            user_id=user_id
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/transaction/{transaction_id}/cancel", response_class=JSONResponse, tags=["Transaction"])
def cancel_transaction(transaction_id: str, user_id: str, db: Session = Depends(get_db)):
    """Cancel a transaction and release locked products with row-level locking"""
    try:
        result = crud.cancel_transaction_and_release_products(
            db=db, 
            transaction_id=transaction_id, 
            user_id=user_id
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put("/product/{product_type_id}/{product_id}/status", response_class=JSONResponse, tags=["Product"])
def update_product_status(product_type_id: int, product_id: int, new_status: str, db: Session = Depends(get_db)):
    """Update product status with row-level locking"""
    try:
        result = crud.update_product_status_with_lock(
            db=db,
            product_type_id=product_type_id,
            product_id=product_id,
            new_status=new_status
        )
        return {"message": f"Product status updated to {new_status}", "product": result}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/product/{product_type_id}/{product_id}/lock-status", response_class=JSONResponse, tags=["Product"])
def get_product_lock_status(product_type_id: int, product_id: int, db: Session = Depends(get_db)):
    """Check if a product is currently locked in any active transaction"""
    try:
        result = crud.get_product_lock_status(
            db=db,
            product_type_id=product_type_id,
            product_id=product_id
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.patch("/transaction/{transaction_id}/shipping-address", response_class=JSONResponse, tags=["Transaction"], dependencies=[Depends(cookie)])
def update_shipping_address(
    transaction_id: str, 
    shipping_update: ShippingAddressUpdate, 
    session_data: schemas.SessionData = Depends(verifier),
    db: Session = Depends(get_db)
):
    """Update shipping address for a transaction"""
    try:
        result = crud.update_transaction_shipping_address(
            db=db,
            transaction_id=transaction_id,
            shipping_update=shipping_update,
            customer_id=str(session_data.UserID)
        )
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))