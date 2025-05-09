from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
import schemas

router = APIRouter()

@router.post("/role/post", response_model=schemas.Role, tags=["Roles"])
def create_role(role: schemas.RoleCreate, db: Session = Depends(get_db)):
    return crud.create_role(db=db, role=role)

@router.get("/roles/get", response_model=List[schemas.RoleBase], tags=["Roles"])
def get_roles(db: Session = Depends(get_db)):
    return crud.get_roles(db=db)

@router.delete("/roles/delete/{role_id}", response_class=JSONResponse, tags=["Roles"])
def delete_user(role_id: str, db: Session = Depends(get_db)):
    deleted = crud.delete_role_by_id(db, role_id)
    if deleted:
        return {"message": "Role deleted successfully"}
    else:
        return {"message": "Role not found or deletion failed"}