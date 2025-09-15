from typing import Dict, List, Union
from fastapi import APIRouter, Depends, HTTPException
from requests import Session
from fastapi.responses import JSONResponse
import crud
from database import get_db
from schemas.marketplace_schemas import CentraSettingDetail, CentraSettingDetailCreate, CentraSettingDetailBase, CentraSettingDetailUpdate

router = APIRouter()

@router.post("/centra_setting_detail/post", response_model=CentraSettingDetail)
def create_centra_setting_detail(centra_setting_detail: CentraSettingDetailCreate, db: Session = Depends(get_db)):
    return crud.create_centra_setting_detail(db=db, centra_setting_detail=centra_setting_detail)

@router.get("/centra_setting_details/get", response_model=List[CentraSettingDetail])
def get_centra_setting_details(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_centra_setting_details(db=db, skip=skip, limit=limit)

@router.get("/centra_setting_detail/get/{setting_detail_id}", response_model=CentraSettingDetail)
def get_centra_setting_detail(setting_detail_id: int, db: Session = Depends(get_db)):
    setting_detail = crud.get_centra_setting_detail_by_id(db=db, setting_detail_id=setting_detail_id)
    if not setting_detail:
        raise HTTPException(status_code=404, detail="Centra setting detail not found")
    return setting_detail

@router.get("/centra_setting_detail/get_user/{user_id}", response_model=List[CentraSettingDetail])
def get_centra_setting_detail(user_id: str, db: Session = Depends(get_db)):
    setting_detail = crud.get_centra_setting_detail_by_user_id(db=db, user_id=user_id)
    if not setting_detail:
        raise HTTPException(status_code=404, detail="Centra setting detail not found")
    return setting_detail

@router.get("/centra_setting_detail/get_user/{user_id}/{item_name}", response_model=List[Dict])
def get_centra_setting_detail(user_id: str, item_name:str, db: Session = Depends(get_db)):
    setting_details = crud.get_centra_setting_detail_by_user_id_and_item(db=db, user_id=user_id, item_name=item_name)
    if not setting_details:
        raise HTTPException(status_code=404, detail="Centra setting detail not found")
    
    # Map results to the desired structure
    result = [{"id": detail.SettingDetailID, "expiry": detail.ExpDayLeft, "discountRate": detail.DiscountRate} for detail in setting_details]
    return result

@router.put("/centra_setting_detail/put/{setting_detail_id}", response_model=CentraSettingDetail)
def update_centra_setting_detail(setting_detail_id: int, setting_detail_update: CentraSettingDetailBase, db: Session = Depends(get_db)):
    updated_setting_detail = crud.update_centra_setting_detail(db=db, setting_detail_id=setting_detail_id, setting_detail_update=setting_detail_update)
    if not updated_setting_detail:
        raise HTTPException(status_code=404, detail="Centra setting detail not found")
    return updated_setting_detail

@router.delete("/centra_setting_detail/delete/{setting_detail_id}", response_class=JSONResponse)
def delete_centra_setting_detail(setting_detail_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_centra_setting_detail(db, setting_detail_id)
    if deleted:
        return {"message": "Centra setting detail deleted successfully"}
    else:
        return {"message": "Centra setting detail not found or deletion failed"}


@router.patch("/centra_settings_detail/patch/{setting_detail_id}", response_model=str)
def update_centra_settings_detail(
    setting_detail_id: int, setting_detail_update: CentraSettingDetailUpdate, db: Session = Depends(get_db)
):
    updated_centra_setting = crud.patch_centra_setting_detail(
        db=db, setting_detail_id = setting_detail_id, setting_detail_update=setting_detail_update
    )
    
    if not updated_centra_setting:
        raise HTTPException(status_code=404, detail="Centra setting detail not found")

    # Return updated fields in the desired format
    return "Patched Successfully"

# Centra Base Settings
from schemas.marketplace_schemas import CentraBaseSettings, CentraBaseSettingsCreate, CentraBaseSettingsBase, CentraBaseSettingUpdate, CentraSettingDetailUpdate

@router.post("/centra_base_settings/post", response_model=CentraBaseSettings)
def create_centra_base_settings(centra_base_settings: CentraBaseSettingsCreate, db: Session = Depends(get_db)):
    return crud.create_centra_base_settings(db=db, centra_base_settings=centra_base_settings)

@router.get("/centra_base_settings/get", response_model=List[CentraBaseSettings])
def get_centra_base_settings(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
    return crud.get_centra_base_settings(db=db, skip=skip, limit=limit)

@router.put("/centra_base_settings/put/{settings_id}", response_model=CentraBaseSettings)
def update_centra_base_settings(settings_id: int, centra_base_settings_update: CentraBaseSettingsBase, db: Session = Depends(get_db)):
    updated_centra_base_settings = crud.update_centra_base_settings(db=db, settings_id=settings_id, centra_base_settings_update=centra_base_settings_update)
    if not updated_centra_base_settings:
        raise HTTPException(status_code=404, detail="Centra Base Setting not found")
    return updated_centra_base_settings

@router.patch("/centra_base_settings/patch/{UserID}/{ProductID}", response_model=List[Dict])
def update_centra_base_settings(
    UserID: str, ProductID: int, setting_detail_update: CentraBaseSettingUpdate, db: Session = Depends(get_db)
):
    updated_centra_setting = crud.patch_centra_base_settings(
        db=db, UserID=UserID, ProductID=ProductID, setting_detail_update=setting_detail_update
    )
    if not updated_centra_setting:
        raise HTTPException(status_code=404, detail="Centra setting detail not found")

    # Return updated fields in the desired format
    return [{"InitialPrice": updated_centra_setting.InitialPrice, "Sellable": updated_centra_setting.Sellable}]

# @router.delete("/centra_initial_price/delete/{initial_price_id}", response_class=JSONResponse, tags=["Centra Initial Prices"])
# def delete_centra_initial_price(initial_price_id: int, db: Session = Depends(get_db)):
#     deleted = crud.delete_centra_initial_price(db, initial_price_id)
@router.delete("/centra_base_settings/delete/{settings_id}", response_class=JSONResponse)
def delete_centra_base_settings(settings_id: int, db: Session = Depends(get_db)):
    deleted = crud.delete_centra_base_settings(db, settings_id)
    if deleted:
        return {"message": "Centra Base Setting deleted successfully"}
    else:
        return {"message": "Centra Base Setting not found or deletion failed"}

@router.get("/centra_base_settings/get_user/{user_id}/{item_name}", response_model=List[Dict])
def get_centra_base_settings_by_user_and_item(user_id: str, item_name: str, db: Session = Depends(get_db)):
    base_settings = crud.get_centra_base_settings_by_user_id_and_items(db=db, user_id=user_id, item_name=item_name)
    if not base_settings:
        raise HTTPException(status_code=404, detail="Centra setting detail not found")
    
    print(base_settings)
    # Map the results correctly by iterating through the base_settings
    result = [{"initialPrice": setting.InitialPrice, "sellable": setting.Sellable} for setting in base_settings]
    
    return result