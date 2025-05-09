from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
import schemas

router = APIRouter()

@router.post("/subtransaction/post", response_model=schemas.SubTransaction, tags=["SubTransaction"])
def create_subtransaction(subtransaction: schemas.SubTransactionCreate, db: Session = Depends(get_db)):
    return crud.create_subtransaction(db=db, subtransaction=subtransaction)

@router.get("/subtransactions/get", response_model=List[schemas.SubTransaction], tags=["SubTransaction"])
def get_subtransactions(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_subtransactions(db=db, skip=skip, limit=limit)

@router.get("/subtransaction/get/{subtransaction_id}", response_model=schemas.SubTransaction, tags=["SubTransaction"])
def get_subtransaction(subtransaction_id: int, db: Session = Depends(get_db)):
    subtransaction = crud.get_subtransaction_by_id(db=db, subtransaction_id=subtransaction_id)
    if not subtransaction:
        raise HTTPException(status_code=404, detail="SubTransaction not found")
    return subtransaction

@router.put("/subtransaction/put/{subtransaction_id}", response_model=schemas.SubTransaction, tags=["SubTransaction"])
def update_subtransaction(subtransaction_id: int, subtransaction_update: schemas.SubTransactionUpdate, db: Session = Depends(get_db)):
    updated_subtransaction = crud.update_subtransaction(db=db, subtransaction_id=subtransaction_id, subtransaction_update=subtransaction_update)
    if not updated_subtransaction:
        raise HTTPException(status_code=404, detail="SubTransaction not found")
    return updated_subtransaction

@router.delete("/subtransaction/delete/{subtransaction_id}", response_class=JSONResponse, tags=["SubTransaction"])
def delete_subtransaction(subtransaction_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_subtransaction(db, subtransaction_id)
    if deleted:
        return {"message": "SubTransaction deleted successfully"}
    else:
        return {"message": "SubTransaction not found or deletion failed"}