from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
import schemas

router = APIRouter()


@router.post("/algorithm/bulkSelectedCentra", response_model=Dict[str, Union[int, Dict[str, List[Union[schemas.SimpleFlour, schemas.SimpleDryLeaves]]]]])
def bulk_item_selection_by_selected_centras(request: schemas.BulkItemSelectionRequest, db: Session = Depends(get_db)):
    try:
        max_value, choices = crud.bulk_algorithm_by_selected_centra(
            db, 
            item_type=request.item_type, 
            target_weight=request.target_weight, 
            users=request.users
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"max_value": max_value, "choices": choices}


@router.get("/algorithm/bulkItem", response_model=Dict[str, Union[int, Dict[str, List[Union[schemas.SimpleFlour, schemas.SimpleDryLeaves]]]]])
def bulk_item_selection_by_items(item_type: str, target_weight: int, db: Session = Depends(get_db)):
    try:
        max_value, choices = crud.bulk_algorithm_by_random_items(db, item_type=item_type, target_weight=target_weight)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"max_value": max_value, "choices": choices}

    