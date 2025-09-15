from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
from schemas.location_schemas import Location, LocationCreate, LocationPatch

router = APIRouter()

@router.post('/location/post', tags=["Location"])
def create_location(location: LocationCreate, db: Session = Depends(get_db)):
    crud.create_location(db, location=location)
    return {"code":"200"}

@router.get('/location/get', response_model=List[Location], tags=["Location"])
def get_location(limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_location(db=db, limit=limit)

@router.get('/location/getuserid/{user_id}', response_model=Location, tags=["Location"])
def get_location_by_user_id(user_id: str, db: Session = Depends(get_db)):
    location = crud.get_location_by_user_id(db=db, user_id=user_id)
    if not location:
        raise HTTPException(status_code=404, detail="location not found")
    return location

@router.patch("/location/patchuserid/{user_id}")
def patch_location_by_user_id(location: LocationPatch, user_id:str, db: Session=Depends(get_db)):
    location = crud.patch_location_by_user_id(db=db, user_id=user_id, location=location)
    return location
    
# @router.delete('/location/delete/{location_id}', tags=["Location"])
# def delete_location_by_id(location_id: int, db: Session = Depends(get_db)):
#     delete = crud.delete_location_by_id(db=db, location_id=location_id)
#     if delete:
#         return {"message": "location deleted successfully"}
#     else:
#         return {"message": "location not found or deletion failed"}
    
