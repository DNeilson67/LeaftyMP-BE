from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
import schemas

router = APIRouter()

@router.post("/admin_settings/post", response_model=schemas.AdminSettings, tags=["Admin Settings"])
def create_admin_settings(admin_settings: schemas.AdminSettingsCreate, db: Session = Depends(get_db)):
    return crud.create_admin_settings(db=db, admin_settings=admin_settings)

@router.get("/admin_settings/get", response_model=schemas.AdminSettings, tags=["Admin Settings"])
def get_admin_settings(db: Session = Depends(get_db)):
    return crud.get_admin_settings(db=db)

@router.put("/admin_settings/put/{admin_settings_id}", response_model=schemas.AdminSettings, tags=["Admin Settings"])
def update_admin_settings(admin_settings_id: int, admin_settings_update: schemas.AdminSettingsBase, db: Session = Depends(get_db)):
    updated_admin_settings = crud.update_admin_settings(db=db, admin_settings_id=admin_settings_id, admin_settings_update=admin_settings_update)
    if not updated_admin_settings:
        raise HTTPException(status_code=404, detail="Admin settings not found")
    return updated_admin_settings