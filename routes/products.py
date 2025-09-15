from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
from schemas.marketplace_schemas import Products, ProductsCreate, ProductsBase

router = APIRouter()

@router.post("/product/post", response_model=Products, tags=["Products"])
def create_product(product: ProductsCreate, db: Session = Depends(get_db)):
    return crud.create_product(db=db, product=product)

@router.get("/products/get", response_model=List[Products], tags=["Products"])
def get_products(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_products(db=db, skip=skip, limit=limit)

@router.get("/product/get/{product_id}", response_model=Products, tags=["Products"])
def get_product(product_id: int, db: Session = Depends(get_db)):
    product = crud.get_product_by_id(db=db, product_id=product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product

@router.put("/product/put/{product_id}", response_model=Products, tags=["Products"])
def update_product(product_id: int, product_update: ProductsBase, db: Session = Depends(get_db)):
    updated_product = crud.update_product(db=db, product_id=product_id, product_update=product_update)
    if not updated_product:
        raise HTTPException(status_code=404, detail="Product not found")
    return updated_product

@router.delete("/product/delete/{product_id}", response_class=JSONResponse, tags=["Products"])
def delete_product(product_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_product(db, product_id)
    if deleted:
        return {"message": "Product deleted successfully"}
    else:
        return {"message": "Product not found or deletion failed"}