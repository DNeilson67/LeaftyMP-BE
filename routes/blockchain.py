from typing import List
from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
from schemas import blockchain_schemas
from schemas.user_schemas import SessionData
from routes.auth import backend, verifier, cookie
from uuid import UUID

router = APIRouter()

@router.get("/blockchain/debug/session", tags=["Blockchain"], dependencies=[Depends(cookie)])
async def debug_session(request: Request, db: Session = Depends(get_db), session_data: SessionData = Depends(verifier)):
    """
    Debug endpoint to check session authentication
    """
    try:
        return {
            "message": "Session found and valid",
            "session_data": {
                "user_id": session_data.UserID,
                "username": session_data.Username,
                "role_id": session_data.RoleID,
                "email": session_data.Email
            },
            "cookies_received": dict(request.cookies)
        }
            
    except Exception as e:
        print("❌ Debug endpoint error:", str(e))
        return JSONResponse(
            status_code=500,
            content={"error": f"Debug error: {str(e)}"}
        )

@router.post("/blockchain/create", tags=["Blockchain"], dependencies=[Depends(cookie)])
def create_blockchain_transaction(
    trx_data: blockchain_schemas.BlockchainTrxCreate, 
    db: Session = Depends(get_db),
    session_data: SessionData = Depends(verifier)
):

    try:
        user_id = session_data.UserID
        
        user = crud.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        # Check if blockchain hash already exists
        existing_trx = crud.get_blockchain_trx_by_hash(db, trx_data.trx_id)
        if existing_trx:
            raise HTTPException(status_code=400, detail="Transaction ID already exists")
        
        blockchain_trx = crud.create_blockchain_trx(db, user_id, trx_data.trx_id)
        
        return JSONResponse(
            status_code=201,
            content={
                "message": "Blockchain transaction created successfully",
                "data": {
                    "user_id": blockchain_trx.UserID,
                    "trx_id": blockchain_trx.TrxId,  # Auto-incrementing ID
                    "blockchain_hash": blockchain_trx.BlockchainHash,  # Actual blockchain transaction hash
                    "created_at": blockchain_trx.CreatedAt.isoformat() if blockchain_trx.CreatedAt else None
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/blockchain/my-transactions", tags=["Blockchain"], dependencies=[Depends(cookie)])
def get_my_blockchain_transactions(
    db: Session = Depends(get_db),
    session_data: SessionData = Depends(verifier)
):
    try:
        user_id = session_data.UserID
        
        user = crud.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        transactions = crud.get_blockchain_trx_by_user_id(db, user_id)
        
        if not transactions:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "No blockchain transactions found for this user",
                    "data": []
                }
            )
        
        transaction_data = [
            {
                "user_id": trx.UserID,
                "trx_id": trx.TrxId,
                "created_at": trx.CreatedAt.isoformat() if trx.CreatedAt else None,
                "username": user.Username
            }
            for trx in transactions
        ]
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Blockchain transactions retrieved successfully",
                "data": transaction_data
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/blockchain/centra/{centra_name}", tags=["Blockchain"], dependencies=[Depends(cookie)])
def get_centra_blockchain_transactions(
    centra_name: str,
    db: Session = Depends(get_db)
):
    try:
        username = centra_name
        user = crud.get_user_by_username(db, username)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        transactions = crud.get_blockchain_trx_by_user_id(db, user.UserID)
        
        if not transactions:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "No blockchain transactions found for this user",
                    "data": []
                }
            )
        
        transaction_data = [
            {
                "user_id": trx.UserID,
                "trx_id": trx.TrxId,
                "created_at": trx.CreatedAt.isoformat() if trx.CreatedAt else None,
                "username": user.Username
            }
            for trx in transactions
        ]
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Blockchain transactions retrieved successfully",
                "data": transaction_data
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/blockchain/transaction/{trx_id}", tags=["Blockchain"], dependencies=[Depends(cookie)])
def get_blockchain_transaction_by_id(
    trx_id: str, 
    db: Session = Depends(get_db),
    session_data: SessionData = Depends(verifier)
):
    """
    Get blockchain transaction details by transaction ID
    """
    try:
        transaction = crud.get_blockchain_trx_by_trx_id(db, trx_id)
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Blockchain transaction not found")
        
        if transaction.UserID != session_data.UserID and session_data.RoleID != 1:
            raise HTTPException(status_code=403, detail="Access denied. You can only access your own transactions")
        
        user = crud.get_user_by_id(db, transaction.UserID)
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Blockchain transaction retrieved successfully",
                "data": {
                    "user_id": transaction.UserID,
                    "trx_id": transaction.TrxId,
                    "created_at": transaction.CreatedAt.isoformat() if transaction.CreatedAt else None,
                    "username": user.Username if user else None,
                    "user_email": user.Email if user else None
                }
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")





@router.get("/blockchain/admin/all", tags=["Blockchain"], dependencies=[Depends(cookie)])
def get_all_blockchain_transactions_admin(
    db: Session = Depends(get_db),
    session_data: SessionData = Depends(verifier)
):
    """
    Get all blockchain transactions (Admin only)
    """
    try:
        if session_data.RoleID != 1:
            raise HTTPException(status_code=403, detail="Access denied. Admin privileges required")
        
        transactions = crud.get_all_blockchain_trx(db)
        
        if not transactions:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "No blockchain transactions found",
                    "data": []
                }
            )
        
        transaction_data = []
        for trx in transactions:
            user = crud.get_user_by_id(db, trx.UserID)
            transaction_data.append({
                "user_id": trx.UserID,
                "trx_id": trx.TrxId,
                "created_at": trx.CreatedAt.isoformat() if trx.CreatedAt else None,
                "username": user.Username if user else None,
                "user_email": user.Email if user else None,
                "user_role_id": user.RoleID if user else None
            })
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "All blockchain transactions retrieved successfully",
                "data": transaction_data
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

@router.get("/blockchain/admin/user/{user_id}", tags=["Blockchain"], dependencies=[Depends(cookie)])
def get_blockchain_transactions_by_user_admin(
    user_id: str,
    db: Session = Depends(get_db),
    session_data: SessionData = Depends(verifier)
):
    """
    Get all blockchain transactions for a specific user (Admin only)
    """
    try:
        if session_data.RoleID != 1:
            raise HTTPException(status_code=403, detail="Access denied. Admin privileges required")
        
        user = crud.get_user_by_id(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        transactions = crud.get_blockchain_trx_by_user_id(db, user_id)
        
        if not transactions:
            return JSONResponse(
                status_code=200,
                content={
                    "message": "No blockchain transactions found for this user",
                    "data": []
                }
            )
        
        transaction_data = [
            {
                "user_id": trx.UserID,
                "trx_id": trx.TrxId,
                "created_at": trx.CreatedAt.isoformat() if trx.CreatedAt else None,
                "username": user.Username
            }
            for trx in transactions
        ]
        
        return JSONResponse(
            status_code=200,
            content={
                "message": "Blockchain transactions retrieved successfully",
                "data": transaction_data
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
