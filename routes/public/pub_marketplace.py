from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException, Query
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
from fastapi_sessions.frontends.implementations import SessionCookie, CookieParameters

router = APIRouter()

@router.get("/marketplace/get", response_model=List)
def get_marketplace_items(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_marketplace_items(db=db, skip=skip, limit=limit)

@router.get("/marketplace/get_by_centra/{centra_name}", response_model=List)
def get_marketplace_items_by_centra(
    centra_name: str, 
    skip: int = 0, 
    limit: int = 10, 
    db: Session = Depends(get_db)
):
    """Get marketplace items from a specific centra"""
    items = crud.get_marketplace_items_by_centra(db=db, centra_name=centra_name, skip=skip, limit=limit)
    
    if not items:
        raise HTTPException(status_code=404, detail=f"No products found for centra '{centra_name}'")
    
    return items

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

@router.get("/marketplace/search_products")
def search_marketplace_products(
    query: str = Query(..., min_length=1),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    results = crud.search_products_by_query(db=db, query=query, skip=skip, limit=limit)

    if not results:
        raise HTTPException(status_code=404, detail="No matching products or users found")

    return [
        {
            "id": r.id, 
            "product_name": r.product_name,
            "weight": r.weight,
            "username": r.username,
            "centra_id": r.centra_id,
            "expiration": r.expiration.isoformat() if r.expiration else None,
        }
        for r in results
    ]
