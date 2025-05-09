from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
import schemas

router = APIRouter()

@router.post("/dryleaves/post", response_model=schemas.DryLeaves)
def create_dry_leaves(dry_leaves: schemas.DryLeavesCreate, db: Session = Depends(get_db)):
    return crud.create_dry_leaves(db=db, dry_leaves=dry_leaves)

@router.get("/dryleaves/get/")
def get_dry_leaves_for_admin(db: Session = Depends(get_db)):
    return crud.get_dry_leaves(db=db)

@router.get("/dryleaves/get/{dry_leaves_id}", response_model=schemas.DryLeaves)
def get_dry_leaves_id(dry_leaves_id: int, db: Session = Depends(get_db)):
    dry_leaves = crud.get_dry_leaves_by_id(db=db, dry_leaves_id=dry_leaves_id)
    if not dry_leaves:
        raise HTTPException(status_code=404, detail="dry leaves not found")
    return dry_leaves

@router.get("/dryleaves/get_by_user/{user_id}", response_model=List[schemas.DryLeaves])
def get_dry_leaves_by_user(user_id: str, db: Session = Depends(get_db)):
    dry_leaves = crud.get_dry_leaves_by_user_id(db, user_id)
    if not dry_leaves:
        raise HTTPException(status_code=404, detail="Dry leaves not found")
    return dry_leaves

@router.delete("/dryleaves/delete/{dry_leaves_id}", response_class=JSONResponse)
def delete_dry_leaves_by_id(dry_leaves_id: int, db: Session = Depends(get_db)):
    delete = crud.delete_dry_leaves_by_id(db=db, dry_leaves_id=dry_leaves_id)
    if delete:
        return {"message": "dry leaves deleted successfully"}
    else:
        return {"message": "dry leaves not found or deletion failed"}

@router.put("/dryleaves/put/{dry_leaves_id}", response_model=schemas.DryLeaves)
def update_dry_leaves(dry_leaves_id: int, dry_leaves: schemas.DryLeavesUpdate, db: Session = Depends(get_db)):
    update_dry_leaves = crud.update_dry_leaves(db=db, dry_leaves_id=dry_leaves_id, dry_leaves_update=dry_leaves)
    if not update_dry_leaves:
        raise HTTPException(status_code=404, detail="dry leaves not found")
    return update_dry_leaves

@router.put("/dryleaves/update_status/{dry_leaves_id}", response_model=schemas.DryLeaves)
def update_dry_leaves_status(dry_leaves_id: int, status_update: schemas.DryLeavesStatusUpdate, db: Session = Depends(get_db)):
    updated_dry_leaves = crud.update_dry_leaves_status(db=db, dry_leaves_id=dry_leaves_id, status_update=status_update)
    if not updated_dry_leaves:
        raise HTTPException(status_code=404, detail="dry leaves not found")
    return updated_dry_leaves
