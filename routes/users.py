from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
import schemas

router = APIRouter()

@router.get("/user/get", response_model=List[schemas.User], tags=["Users"])
def get_users(db: Session = Depends(get_db)):
    # print(f"Fetching users with skip={skip}, limit={limit}")
    users = crud.get_users(db)
    # print(f"Fetched {len(users)} users")
    return users

@router.get("/user/count", response_model=int, tags=["Users"])
def get_user_count(db: Session = Depends(get_db)):
    count = crud.get_user_count(db)
    print(f"Total user count: {count}")
    return count

@router.get("/user/get_role/{role_id}", response_model=List[schemas.User], tags=["Users"])
def get_user(role_id: int, db: Session = Depends(get_db)):
    role = crud.get_user_by_role(db, role_id)
    if not role:
        raise HTTPException(status_code=400, detail="Role does not exist")
    else:
        users = crud.get_user_by_role(db, role_id)
        return users

@router.get("/user/get_user/{user_id}", response_model=schemas.User, tags=["Users"])
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    return user

@router.get("/user/get_user_email/{email}", response_model=Dict, tags=["Users"])
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_email(db, email)
    return {"code": "200", "exist": True if user else False}

@router.get("/user/get_user_details_email/{email}", tags=["Users"])
def get_user_by_email(email: str, db: Session = Depends(get_db)):
    return crud.get_user_by_email(db, email)
    # return {"code": "200", "exist": True if user else False}


@router.get('/users_with_shipments', tags=["Users", "Shipment"])
def get_users_with_shipments(db: Session = Depends(get_db)):
    users = crud.get_users_with_shipments(db)
    return users

@router.put('/user/put/{user_id}', response_model=schemas.UserUpdate, tags=["Users"])
def update_user(user_id: str, user: schemas.UserUpdate, db: Session = Depends(get_db)):
    updated_user = crud.update_user(db=db, user_id=user_id, user_update=user)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User does not exist")
    return updated_user

@router.put('/user/update_phone/{user_id}', response_model=schemas.User, tags=["Users"])
def update_user_phone_endpoint(user_id: str, phone_update: schemas.UserPhoneUpdate, db: Session = Depends(get_db)):
    updated_user = crud.update_user_phone(db=db, user_id=user_id, PhoneNumber=phone_update.PhoneNumber)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User not found")
    return updated_user

@router.put('/user/admin_put/{user_id}', response_model=schemas.User, tags=["Users"])
def update_user(user_id: str, user: schemas.AdminUserUpdate, db: Session = Depends(get_db)):
    try:
        updated_user = crud.admin_update_user(db=db, user_id=user_id, user_update=user)
        if not updated_user:
            raise HTTPException(status_code=404, detail="User does not exist")
        return updated_user
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.put('/user/update_role/{user_id}', response_model=schemas.User, tags=["Users"])
def update_user_role(user_id: str, role_update: schemas.UserRoleUpdate, db: Session = Depends(get_db)):
    role_name_to_id = {
        "Centra": 1,
        "Harbor": 2,
        "Company": 3,
        "Admin": 4,
        "Customer": 5,
        "Rejected": 6
    }
    role_id = role_name_to_id.get(role_update.RoleName)
    print(role_id)
    if role_id is None:
        raise HTTPException(status_code=400, detail="Invalid role name")

    updated_user = crud.update_user_role(db=db, user_id=user_id, role_id=role_id)
    if not updated_user:
        raise HTTPException(status_code=404, detail="User does not exist or role does not exist")
    return updated_user


@router.delete("/user/delete/{user_id}", response_class=JSONResponse, tags=["Users"])
def delete_user(user_id: str, db: Session = Depends(get_db)):
    deleted = crud.delete_user_by_id(db, user_id)
    if deleted:
        return {"message": "User deleted successfully"}
    else:
        return {"message": "User not found or deletion failed"}
