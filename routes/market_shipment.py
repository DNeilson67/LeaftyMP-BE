from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
from schemas.transaction_schemas import MarketShipment, MarketShipmentCreate, MarketShipmentUpdate

router = APIRouter()

@router.post("/market_shipment/post", tags=["MarketShipment"])
def create_market_shipment(market_shipment: MarketShipmentCreate, db: Session = Depends(get_db)):
    return crud.create_market_shipment(db=db, market_shipment=market_shipment)

@router.get("/market_shipments/get", response_model=List[MarketShipment], tags=["MarketShipment"])
def get_market_shipments(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_market_shipments(db=db, skip=skip, limit=limit)

@router.get("/market_shipments/centra/{centra_id}", response_model=List[MarketShipment], tags=["MarketShipment"])
def get_market_shipments_by_centra(centra_id: str, skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    """Get market shipments for a specific centra"""
    return crud.get_market_shipments_by_centra_id(db=db, centra_id=centra_id, skip=skip, limit=limit)

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