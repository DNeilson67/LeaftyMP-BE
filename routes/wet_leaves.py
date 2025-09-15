from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
from schemas.leaves_schemas import WetLeaves, WetLeavesCreate, WetLeavesUpdate, WetLeavesStatusUpdate

router = APIRouter()

@router.post("/wetLeaves/post", response_model=WetLeaves)
def create_wet_leaves(wet_leaves: WetLeavesCreate, db: Session = Depends(get_db)):
    return crud.create_wet_leaves(db=db, wet_leaves=wet_leaves)

@router.get("/wetleaves/get")
def get_wet_leaves_for_admin(db: Session = Depends(get_db)):
    return crud.get_wet_leaves(db=db)

@router.get("/wetleaves/get/{wet_leaves_id}", response_model=WetLeaves)
def get_wet_leaves_id(wet_leaves_id: int, db: Session = Depends(get_db)):
    wet_leaves = crud.get_wet_leaves_by_id(db=db, wet_leaves_id=wet_leaves_id)
    if not wet_leaves:
        raise HTTPException(status_code=404, detail="wet leaves not found")
    return wet_leaves

@router.get("/wetleaves/get_by_user/{user_id}", response_model=List[WetLeaves])
def get_wet_leaves_by_user(user_id: str, db: Session = Depends(get_db)):
    wet_leaves = crud.get_wet_leaves_by_user_id(db, user_id)
    if not wet_leaves:
        raise HTTPException(status_code=404, detail="wet leaves not found")
    return wet_leaves

@router.get('/wetleaves/sum_weight_today/{user_id}')
def get_sum_weight_wet_leaves_by_user_today(user_id: str, db: Session = Depends(get_db)):
    total_weight = crud.sum_weight_wet_leaves_by_user_today(db, user_id)
    return {"user_id": user_id, "total_weight_today": total_weight}

@router.delete("/wetleaves/delete/{wet_leaves_id}", response_class=JSONResponse)
def delete_wet_leaves_by_id(wet_leaves_id: int, db: Session = Depends(get_db)):
    delete = crud.delete_wet_leaves_by_id(db=db, wet_leaves_id=wet_leaves_id)
    if delete:
        return {"message": "wet leaves deleted successfully"}
    else:
        return {"message": "wet leaves not found or deletion failed"}

@router.put("/wetleaves/put/{wet_leaves_id}", response_model=WetLeaves)
def update_wet_leaves(wet_leaves_id: int, wet_leaves: WetLeavesUpdate, db: Session = Depends(get_db)):
    update_wet_leaves = crud.update_wet_leaves(db=db, wet_leaves_id=wet_leaves_id, wet_leaves_update=wet_leaves)
    if not update_wet_leaves:
        raise HTTPException(status_code=404, detail="wet leaves not found")
    return update_wet_leaves

@router.put("/wetleaves/update_status/{wet_leaves_id}", response_model=WetLeaves)
def update_wet_leaves_status(wet_leaves_id: int, status_update: WetLeavesStatusUpdate, db: Session = Depends(get_db)):
    updated_wet_leaves = crud.update_wet_leaves_status(db=db, wet_leaves_id=wet_leaves_id, status_update=status_update)
    if not updated_wet_leaves:
        raise HTTPException(status_code=404, detail="wet leaves not found")
    return updated_wet_leaves
