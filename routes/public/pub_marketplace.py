from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException, Query
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
import schemas
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters

router = APIRouter()

@router.get("/marketplace/get", response_model=List)
def get_marketplace_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_marketplace_items(db=db, skip=skip, limit=limit)

@router.get("/marketplace/get_product_details")
def get_marketplace_item(
    product_id: int = Query(...),
    product_name: str = Query(...),
    username: str = Query(...),
    db: Session = Depends(get_db)
):
    # print(product_id, product_name, username)
    
    item = crud.get_product_details_by_product_id_and_product_name_and_username(
        db=db,
        product_id=product_id,
        product_name=product_name,
        username=username
    )
    
    if not item:
        raise HTTPException(status_code=404, detail="Item not found")
    return item