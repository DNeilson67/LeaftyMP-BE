from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from requests import Session

import crud
from database import get_db

router = APIRouter()

@router.get("/items/all", tags=["Items"])
def read_all_items(item_type: str, db: Session = Depends(get_db)):
    try:
        items = crud.get_all_items(db, item_type=item_type)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return items

@router.get("/items/random", tags=["Items"])
def read_random_items(item_type: str, limit: int, db: Session = Depends(get_db)):
    try:
        items = crud.get_random_items(db, item_type=item_type, limit=limit)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    return items
