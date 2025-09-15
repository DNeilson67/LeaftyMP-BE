from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db

router = APIRouter()

@router.get('/statistics/all', tags=["Statistics"])
def retrieve_all_stats(db: Session = Depends(get_db)):
    sum_wet_leaves = crud.sum_total_wet_leaves(db)
    sum_dry_leaves = crud.sum_total_dry_leaves(db)
    sum_flour = crud.sum_total_flour(db)
    sum_shipment_quantity = crud.sum_total_shipment_quantity(db)
    
    return {
        "sum_wet_leaves": sum_wet_leaves,
        "sum_dry_leaves": sum_dry_leaves,
        "sum_flour": sum_flour,
        "sum_shipment_quantity": sum_shipment_quantity
    }

@router.get('/statistics/all_no_format', tags=["Statistics"])
def retrieve_all_stats_no_format(db: Session = Depends(get_db)):
    sum_wet_leaves = crud.sum_total_wet_leaves(db)
    sum_dry_leaves = crud.sum_total_dry_leaves(db)
    sum_flour = crud.sum_total_flour(db)
    sum_shipment_quantity = crud.sum_total_shipment_quantity(db)
    
    return {
        "sum_wet_leaves": sum_wet_leaves,
        "sum_dry_leaves": sum_dry_leaves,
        "sum_flour": sum_flour,
        "sum_shipment_quantity": sum_shipment_quantity
    }
    
@router.get('/centra/statistics/{user_id}', tags = ["Statistics"])
def retrieve_centra_stats(user_id: str, db: Session = Depends(get_db)):
    sum_wet_leaves = crud.sum_get_wet_leaves_by_user_id(db, user_id)
    sum_dry_leaves = crud.sum_get_dry_leaves_by_user_id(db, user_id)
    sum_flour = crud.sum_get_flour_by_user_id(db, user_id)
    sum_shipment_quantity = crud.sum_get_shipment_quantity_by_user_id(db, user_id)
    return {
        "sum_wet_leaves": sum_wet_leaves,
        "sum_dry_leaves": sum_dry_leaves,
        "sum_flour": sum_flour,
        "sum_shipment_quantity": sum_shipment_quantity
    }

