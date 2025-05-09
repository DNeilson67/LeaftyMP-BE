from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
import schemas

router = APIRouter()

@router.post("/flour/post", response_model=schemas.Flour, tags=["Flour"])
def create_flour(flour: schemas.FlourCreate, db: Session = Depends(get_db)):
    return crud.create_flour(db=db, flour=flour)

@router.get("/flour/get", tags=["Flour"])
def get_flour_for_admin(db: Session = Depends(get_db)):
    return crud.get_flour(db=db)

@router.get("/flour/get/{flour_id}", response_model=schemas.Flour, tags=["Flour"])
def get_flour_by_id(flour_id: int, db: Session = Depends(get_db)):
    flour = crud.get_flour_by_id(db=db, flour_id=flour_id)
    if not flour:
        raise HTTPException(status_code=404, detail="flour not found")
    else:
        return flour

@router.get("/flour/get_by_user/{user_id}", response_model=List[schemas.Flour], tags=["Flour"])
def get_flour_by_user(user_id: str, db: Session = Depends(get_db)):
    flour = crud.get_flour_by_user_id(db, user_id)
    if not flour:
        raise HTTPException(status_code=404, detail="flour not found")
    return flour

@router.delete("/flour/delete/{flour_id}", response_class=JSONResponse, tags=["Flour"])
def delete_flour_by_id(flour_id: int, db: Session = Depends(get_db)):
    delete = crud.delete_flour_by_id(db=db, flour_id=flour_id)
    if delete:
        return {"message": "flour deleted successfully"}
    else:
        return {"message": "flour not found or deletion failed"}

@router.put("/flour/put/{flour_id}", response_model=schemas.Flour, tags=["Flour"])
def update_flour(flour_id: int, flour: schemas.FlourUpdate, db: Session = Depends(get_db)):
    update_flour = crud.update_flour(db=db, flour_id=flour_id, flour_update=flour)
    if not update_flour:
        raise HTTPException(status_code=404, detail="flour not found")
    return update_flour

@router.put("/flour/update_status/{flour_id}", response_model=schemas.Flour, tags=["Flour"])
def update_flour_status(flour_id: int, status_update: schemas.FlourStatusUpdate, db: Session = Depends(get_db)):
    updated_flour = crud.update_flour_status(db=db, flour_id=flour_id, status_update=status_update)
    if not updated_flour:
        raise HTTPException(status_code=404, detail="flour not found")
    return updated_flour