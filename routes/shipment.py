from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
import schemas
import bcrypt

router = APIRouter()

@router.post('/shipment/post', response_model=schemas.Shipment, tags=["Shipment"])
def create_shipment(shipment: schemas.ShipmentCreate, db: Session = Depends(get_db)):
    return crud.create_shipment(db=db, shipment=shipment)

@router.get('/shipment/get', response_model=List[schemas.Shipment], tags=["Shipment"])
def get_shipment(limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_shipment(db=db, limit=limit)

@router.get('/shipment/getid/{shipment_id}', response_model=schemas.Shipment, tags=["Shipment"])
def get_shipment_by_id(shipment_id: int, db: Session = Depends(get_db)):
    shipment = crud.get_shipment_by_id(db=db, shipment_id=shipment_id)
    if not shipment:
        raise HTTPException(status_code=404, detail="shipment not found")
    return shipment

@router.get("/shipment/get_by_user/{user_id}", response_model=List[schemas.Shipment], tags=["Shipment"])
def get_shipment_by_user(user_id: str, db: Session = Depends(get_db)):
    shipment_data = crud.get_shipment_by_user_id(db, user_id)
    if not shipment_data:
        raise HTTPException(status_code=404, detail="shipments not found")
    return shipment_data

@router.get("/shipments/ids", response_model=List[int], tags=["Shipment"])
def get_all_shipment_ids(db: Session = Depends(get_db)):
    shipments = crud.get_all_shipment_ids(db)
    print(f"All shipment IDs: {[shipment.ShipmentID for shipment in shipments]}")
    return [shipment.ShipmentID for shipment in shipments]

# Endpoint to compare shipment IDs
@router.get("/check_shipment_ids", response_model=List[str])
def check_shipment_ids(db: Session = Depends(get_db)):
    shipment_ids = crud.get_shipment_ids_with_date_but_no_checkin(db)
    print(f"Fetched shipment IDs: {shipment_ids}")

    # Example hashed ID to compare
    known_shipment_id = "known_shipment_id"
    hashed_shipment_id = bcrypt.hashpw(known_shipment_id.encode('utf-8'), bcrypt.gensalt())
    print(f"Hashed shipment ID: {hashed_shipment_id}")

    def brute_force_check(shipment_id):
        if bcrypt.checkpw(shipment_id.encode('utf-8'), hashed_shipment_id):
            return shipment_id
        else:
            print(f"No match for shipment ID: {shipment_id}")
            return None

    valid_shipment_ids = [brute_force_check(str(shipment_id)) for shipment_id in shipment_ids]
    valid_shipment_ids = list(filter(None, valid_shipment_ids))  # Filter out None values
    print(f"Valid shipment IDs: {valid_shipment_ids}")
    return valid_shipment_ids

@router.put("/shipment/put/{shipment_id}", response_model=schemas.Shipment, tags=["Shipment"])
def update_shipment(shipment_id: int, shipment_update: schemas.ShipmentUpdate, db: Session = Depends(get_db)):
    db_shipment = crud.update_shipment(db, shipment_id, shipment_update)
    if db_shipment is None:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return db_shipment

@router.put("/shipment/update_date/{shipment_id}", response_model=schemas.Shipment, tags=["Shipment"])
def update_shipment_date(shipment_id: int, shipment_date_update: schemas.ShipmentDateUpdate, db: Session = Depends(get_db)):
    updated_shipment = crud.update_shipment_date(db=db, shipment_id=shipment_id, shipment_date_update=shipment_date_update)
    if not updated_shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return updated_shipment

@router.put("/shipment/update_check_in/{shipment_id}", response_model=schemas.Shipment, tags=["Shipment"])
def update_shipment_check_in(shipment_id: int, check_in_update: schemas.ShipmentCheckInUpdate, db: Session = Depends(get_db)):
    updated_shipment = crud.update_shipment_check_in(db=db, shipment_id=shipment_id, check_in_update=check_in_update)
    if not updated_shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return updated_shipment

@router.put("/shipment/update_rescalled_weight/{shipment_id}", response_model=schemas.Shipment, tags=["Shipment"])
def update_shipment_rescalled_weight(shipment_id: int, update_data: schemas.ShipmentRescalledWeightUpdate, db: Session = Depends(get_db)):
    updated_shipment = crud.update_shipment_rescalled_weight_and_date(db=db, shipment_id=shipment_id, update_data=update_data)
    if not updated_shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return updated_shipment

@router.put("/shipment/update_harbor_reception/{shipment_id}", response_model=schemas.Shipment, tags=["Shipment"])
def update_shipment_harbor_reception(shipment_id: int, update_data: schemas.ShipmentHarborReceptionUpdate, db: Session = Depends(get_db)):
    updated_shipment = crud.update_shipment_harbor_reception(db=db, shipment_id=shipment_id, update_data=update_data)
    if not updated_shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return updated_shipment

@router.put("/shipment/update_centra_reception/{shipment_id}", response_model=schemas.Shipment, tags=["Shipment"])
def update_shipment_centra_reception(shipment_id: int, update_data: schemas.ShipmentCentraReceptionUpdate, db: Session = Depends(get_db)):
    updated_shipment = crud.update_shipment_centra_reception(db=db, shipment_id=shipment_id, update_data=update_data)
    if not updated_shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    return updated_shipment

@router.delete('/shipment/delete/{shipment_id}', tags=["Shipment"])
def delete_shipment_by_id(shipment_id: int, db: Session = Depends(get_db)):
    delete = crud.delete_shipment_by_id(db=db, shipment_id=shipment_id)
    if delete:
        return {"message": "shipment deleted successfully"}
    else:
        return {"message": "shipment not found or deletion failed"}
    
@router.get("/shipment_flour_association/get", response_model=List[schemas.ShipmentFlourAssociation], tags=["ShipmentFlourAssociation"])
def get_shipment_flour_associations(db: Session = Depends(get_db)):
    return crud.get_shipment_flour_associations(db)