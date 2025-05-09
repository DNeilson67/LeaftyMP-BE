from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
import schemas

router = APIRouter()

@router.post("/courier/post", response_model=schemas.Courier, tags=["Courier"])
def create_courier(courier: schemas.CourierCreate, db: Session = Depends(get_db)):
    return crud.create_courier(db, courier)

@router.get("/courier/get", response_model=List[schemas.Courier], tags=["Courier"])
def get_courier(db: Session = Depends(get_db)):
    return crud.get_couriers(db)

@router.get("/courier/get/{courier_id}", response_model=schemas.Courier, tags=["Courier"])
def get_courier_by_courier_id(courier_id:int, db: Session = Depends(get_db)):
    return crud.get_courier_by_id(db, courier_id)   

@router.delete("/courier/delete/{courier_id}", response_class=JSONResponse, tags=["Courier"])
def delete_courier(courier_id: int, db: Session = Depends(get_db)):
    delete = crud.delete_courier(db=db, courier_id=courier_id)
    if delete:
        return {"message": "Courier deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail="Courier not found or deletion failed")
