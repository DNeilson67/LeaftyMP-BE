from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
from schemas.finance_schemas import CentraFinance, CentraFinanceCreate, CentraFinanceBase

router = APIRouter()

@router.post("/centra_finance/post", response_model=CentraFinance, tags=["Centra Finance"])
def create_centra_finance(centra_finance: CentraFinanceCreate, db: Session = Depends(get_db)):
    return crud.create_centra_finance(db=db, centra_finance=centra_finance)

@router.get("/centra_finances/get", response_model=List[CentraFinance], tags=["Centra Finance"])
def get_centra_finances(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_centra_finances(db=db, skip=skip, limit=limit)

@router.get("/centra_finance/get/{finance_id}", response_model=CentraFinance, tags=["Centra Finance"])
def get_centra_finance(finance_id: int, db: Session = Depends(get_db)):
    finance = crud.get_centra_finance_by_id(db=db, finance_id=finance_id)
    if not finance:
        raise HTTPException(status_code=404, detail="Centra Finance record not found")
    return finance

@router.put("/centra_finance/put/{finance_id}", response_model=CentraFinance, tags=["Centra Finance"])
def update_centra_finance(finance_id: int, centra_finance_update: CentraFinanceBase, db: Session = Depends(get_db)):
    updated_finance = crud.update_centra_finance(db=db, finance_id=finance_id, centra_finance_update=centra_finance_update)
    if not updated_finance:
        raise HTTPException(status_code=404, detail="Centra Finance record not found")
    return updated_finance

@router.get("/centra_finance/get_user/{user_id}", response_model=CentraFinance, tags=["Centra Finance"])
def get_centra_finance(user_id: str, db: Session = Depends(get_db)):
    finance = crud.get_centra_finance_by_userid(db=db, UserID=user_id)
    if not finance:
        raise HTTPException(status_code=404, detail="Centra Finance record not found")
    return finance

@router.delete("/centra_finance/delete/{finance_id}", response_class=JSONResponse, tags=["Centra Finance"])
def delete_centra_finance(finance_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_centra_finance(db, finance_id)
    if deleted:
        return {"message": "Centra Finance record deleted successfully"}
    else:
        return {"message": "Centra Finance record not found or deletion failed"}
