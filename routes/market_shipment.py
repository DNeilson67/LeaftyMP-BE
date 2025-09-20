from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
from schemas.transaction_schemas import MarketShipment, MarketShipmentCreate, MarketShipmentUpdate, MarketShipmentWithCentra
from schemas.user_schemas import SessionData
from routes.auth import verifier, cookie

router = APIRouter()

@router.post("/market_shipment/post", tags=["MarketShipment"])
def create_market_shipment(market_shipment: MarketShipmentCreate, db: Session = Depends(get_db)):
    return crud.create_market_shipment(db=db, market_shipment=market_shipment)

@router.get("/market_shipments/get", response_model=List[MarketShipmentWithCentra], tags=["MarketShipment"])
def get_market_shipments(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_market_shipments_with_centra(db=db, skip=skip, limit=limit)

@router.get("/market_shipments/centra/{centra_id}", response_model=List[MarketShipmentWithCentra], tags=["MarketShipment"])
def get_market_shipments_by_centra(centra_id: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get market shipments for a specific centra"""
    return crud.get_market_shipments_by_centra_id(db=db, centra_id=centra_id, skip=skip, limit=limit)

@router.get("/market_shipments/debug/session", dependencies=[Depends(cookie)], tags=["MarketShipment"])
def debug_user_session(session_data: SessionData = Depends(verifier)):
    """Debug endpoint to check current user session"""
    return {
        "user_id": session_data.UserID,
        "username": session_data.Username,
        "role_id": session_data.RoleID,
        "email": session_data.Email,
        "is_centra": session_data.RoleID == 1
    }

@router.get("/market_shipments/user", response_model=List[MarketShipmentWithCentra], dependencies=[Depends(cookie)], tags=["MarketShipment"])
def get_market_shipments_by_user_centra(skip: int = 0, limit: int = 10, db: Session = Depends(get_db), session_data: SessionData = Depends(verifier)):
    """Get market shipments for current user's centra from session - CENTRA USERS ONLY"""
    # Debug: Log session data
    print(f"Session Debug - UserID: {session_data.UserID}, RoleID: {session_data.RoleID}, Username: {session_data.Username}")
    
    # Restrict access to centra users only (RoleID == 1)
    if session_data.RoleID != 1:
        print(f"Access denied - User {session_data.Username} has RoleID {session_data.RoleID}, expected 1")
        raise HTTPException(status_code=403, detail=f"Access denied. This endpoint is only available for centra users. Your role: {session_data.RoleID}")
    
    # For centra users, UserID is the CentraID
    user_centra_id = session_data.UserID
    print(f"Fetching market shipments for centra: {user_centra_id}")
    return crud.get_market_shipments_by_centra_id(db=db, centra_id=user_centra_id, skip=skip, limit=limit)

@router.get("/market_shipment/get/{market_shipment_id}", response_model=MarketShipment, tags=["MarketShipment"])
def get_market_shipment(market_shipment_id: int, db: Session = Depends(get_db)):
    market_shipment = crud.get_market_shipment_by_id(db=db, market_shipment_id=market_shipment_id)
    if not market_shipment:
        raise HTTPException(status_code=404, detail="MarketShipment not found")
    return market_shipment

@router.put("/market_shipment/put/{market_shipment_id}", response_model=MarketShipment, tags=["MarketShipment"])
def update_market_shipment(market_shipment_id: int, market_shipment_update: MarketShipmentUpdate, db: Session = Depends(get_db)):
    updated_market_shipment = crud.update_market_shipment(db=db, market_shipment_id=market_shipment_id, market_shipment_update=market_shipment_update)
    if not updated_market_shipment:
        raise HTTPException(status_code=404, detail="MarketShipment not found")
    return updated_market_shipment

@router.put("/market_shipment/{market_shipment_id}/status", response_model=MarketShipment, tags=["MarketShipment"])
def update_market_shipment_status(market_shipment_id: int, status: str, db: Session = Depends(get_db)):
    """Update the status of a market shipment"""
    updated_market_shipment = crud.update_market_shipment_status(db=db, market_shipment_id=market_shipment_id, status=status)
    if not updated_market_shipment:
        raise HTTPException(status_code=404, detail="MarketShipment not found")
    return updated_market_shipment

@router.delete("/market_shipment/delete/{market_shipment_id}", response_class=JSONResponse, tags=["MarketShipment"])
def delete_market_shipment(market_shipment_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_market_shipment(db, market_shipment_id)
    if deleted:
        return {"message": "MarketShipment deleted successfully"}
    else:
        return {"message": "MarketShipment not found or deletion failed"}