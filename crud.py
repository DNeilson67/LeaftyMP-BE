import bcrypt
from sqlalchemy import cast, Date, and_
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session
from datetime import datetime, timedelta    
from fastapi import HTTPException, Depends
from sqlalchemy.sql import func
from typing import List, Optional
import models
import schemas
import uuid

#otp
def create_otp(db: Session, otp: schemas.OTPCreate):
    db_otp = models.OTP(
        email=otp.email,
        otp_code=otp.otp_code,
        expires_at=datetime.now() + timedelta(minutes=2)
    )
    db.add(db_otp)
    db.commit()
    db.refresh(db_otp)
    return db_otp

def get_otp_by_email(db: Session, email: str):
    return db.query(models.OTP).filter(models.OTP.email == email).first()

def delete_otp(db: Session, email: str):
    db.query(models.OTP).filter(models.OTP.email == email).delete()
    db.commit()

#sessions
def create_session(db: Session, session_id:str, user_id: str):
    user = db.query(models.User).filter(models.User.UserID == user_id).first()
    
    if user is None:
        raise ValueError(f"No user found with user_id: {user_id}")
    
    user_role = user.RoleID
    user_email = user.Email

    db_session = models.SessionData(session_id=session_id, user_id = user_id, user_role = user_role, user_email = user_email)
    db.add(db_session)
    db.commit()

def check_session(db: Session, session_id: str):
    db_session = db.query(models.SessionData).filter(session_id=session_id)
    return db_session

def delete_session(db: Session):
    db.query(models.SessionData).delete()
    db.commit()

# users
def create_user(db: Session, user: schemas.UserCreate):
    user_uuid = str(uuid.uuid4())
    
    hashed_password = bcrypt.hashpw(user.Password.encode(), bcrypt.gensalt(rounds=10)).decode()

    db_user = models.User(
        **user.dict(exclude={"location_address", "longitude", "latitude", "Password"}),
        Password = hashed_password,
        UserID=user_uuid
    )
    
    db_location = models.Location(
        user_id=user_uuid,
        location_address=user.location_address,
        longitude=user.longitude,
        latitude=user.latitude
    )

    # Add user
    db.add(db_user)
    db.commit()
    db.refresh(db_user)

    # Add location
    db.add(db_location)
    db.commit()
    db.refresh(db_location)

    return db_user  # or return both if needed

def get_user_details_by_email(db: Session, Email: str):
    return db.query(models.User).filter(models.User.Email == Email).first()

def get_user_by_role(db: Session, RoleID: int):
    return db.query(models.User).filter(models.User.RoleID == RoleID).all()

def get_users(db: Session):
    users = db.query(models.User).all()
    return users

def get_user_count(db: Session):
    count = db.query(models.User).count()
    print(f"Total user count in database: {count}")
    return count

def get_user_by_id(db: Session, user_id: str):
    return db.query(models.User).filter(cast(models.User.UserID, UUID) == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.Email == email).first()

# def get_user_exist_by_email(db: Session, email: str) -> bool:
#     return db.query(models.User).filter(models.User.Email == email).first() is not None

def update_user(db: Session, user_id: uuid.UUID, user_update: schemas.UserUpdate):
    user = db.query(models.User).filter(models.User.UserID == user_id).first()
    if not user:
        return None
    user.Username = user_update.Username
    user.Email = user_update.Email
    hashed_password = bcrypt.hashpw(user_update.Password.encode(), bcrypt.gensalt(rounds=10)).decode()
    user.Password = hashed_password
    db.commit()
    db.refresh(user)
    return user

def admin_update_user(db: Session, user_id: uuid.UUID, user_update: schemas.AdminUserUpdate):
    user = db.query(models.User).filter(models.User.UserID == user_id).first()
    if not user:
        return None
    if user_update.Username is not None:
        user.Username = user_update.Username
    if user_update.Email is not None:
        user.Email = user_update.Email
    if user_update.PhoneNumber is not None:
        user.PhoneNumber = user_update.PhoneNumber
    if user_update.RoleName is not None:
       role_name_to_id = {
        "Centra": 1,
        "Harbor": 2,
        "Company": 3,
        "Admin": 4,
        "Customer": 5,
        "Rejected": 6
    }
    role = role_name_to_id.get(user_update.RoleName)
    if role:
        user.RoleID = role
    db.commit()
    db.refresh(user)
    return user

def update_user_role(db: Session, user_id: str, role_id: int):
    user = db.query(models.User).filter(models.User.UserID == user_id).first()
    if not user:
        return None
    user.RoleID = role_id
    db.commit()
    db.refresh(user)
    return user

def update_user_phone(db: Session, user_id: str, PhoneNumber: int):
    user = db.query(models.User).filter(models.User.UserID == user_id).first()
    if not user:
        return None
    user.PhoneNumber = PhoneNumber
    db.commit()
    db.refresh(user)
    return user

def delete_user_by_id(db: Session, user_id: str):
    db_user = db.query(models.User).filter(models.User.UserID == user_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# roles
def create_role(db: Session, role: schemas.RoleCreate):
    db_role = models.RoleModel(**role.dict())
    db.add(db_role)
    db.commit()
    db.refresh(db_role)
    return db_role

def get_role(db: Session, role_id: int):
    return db.query(models.RoleModel).filter(models.RoleModel.RoleID == role_id).first()

def get_roles(db: Session):
    return db.query(models.RoleModel).all()

def delete_role_by_id(db: Session, role_id: str):
    db_user = db.query(models.RoleModel).filter(models.RoleModel.RoleID == role_id).first()
    if db_user:
        db.delete(db_user)
        db.commit()
        return True
    return False

# courier
def create_courier(db: Session, courier: schemas.CourierCreate):
    db_courier = models.Courier(**courier.dict())
    db.add(db_courier)
    db.commit()
    db.refresh(db_courier)
    return db_courier

def get_couriers(db: Session):
    return db.query(models.Courier).all()

def get_courier_by_id(db: Session, courier_id: int):
    return db.query(models.Courier).filter(models.Courier.CourierID == courier_id).first()

def delete_courier(db: Session, courier_id: int):
    courier_delete = db.query(models.Courier).filter(models.Courier.CourierID == courier_id).first()
    if courier_delete:
        db.delete(courier_delete)
        db.commit()
        return True
    return False

# wet leaves
def create_wet_leaves(db: Session, wet_leaves: schemas.WetLeavesCreate):
    db_wet_leaves = models.WetLeaves(**wet_leaves.dict())
    db.add(db_wet_leaves)
    db.commit()
    db.refresh(db_wet_leaves)
    return db_wet_leaves
    
def get_wet_leaves(db: Session):
    results = (
        db.query(
            models.WetLeaves.WetLeavesID,
            models.WetLeaves.Weight,
            models.WetLeaves.Expiration,
            models.WetLeaves.Status,
            models.User.Username  # Include Username from User table
        )
        .join(models.User, models.WetLeaves.UserID == models.User.UserID)
        .all()
    )

    # Convert results into dictionaries
    return [dict(row._mapping) for row in results]
    # return db.query(models.WetLeaves).limit(limit).all()

def get_wet_leaves_by_id(db: Session, wet_leaves_id: int):
    return db.query(models.WetLeaves).filter(models.WetLeaves.WetLeavesID == wet_leaves_id).first()

def get_wet_leaves_by_user_id(db: Session, user_id: str):
    return db.query(models.WetLeaves).filter(cast(models.WetLeaves.UserID, UUID) == user_id).all()


def sum_weight_wet_leaves_by_user_today(db: Session, user_id: str):
    today = datetime.now().date()
    result = db.query(func.sum(models.WetLeaves.Weight)).filter(
        and_(
            cast(models.WetLeaves.UserID, UUID) == user_id,
            cast(models.WetLeaves.ReceivedTime, Date) == today
        )
    ).scalar()
    return result or 0

def sum_total_wet_leaves(db: Session):
    wet_leaves_entries = db.query(models.WetLeaves).all()
    sum_wet_leaves = int(sum(entry.Weight for entry in wet_leaves_entries))
    return sum_wet_leaves


def sum_get_wet_leaves_by_user_id(db: Session, user_id: str):
    total_weight = (
        db.query(func.sum(models.WetLeaves.Weight))
        .filter(models.WetLeaves.UserID == user_id)
        .scalar()
    )

    return int(total_weight or 0)

def get_wet_leaves_by_user_and_id(db: Session, user_id: str, wet_leaves_id: int):
    return db.query(models.WetLeaves).filter(models.WetLeaves.UserID == user_id, models.WetLeaves.WetLeavesID == wet_leaves_id).first()

def delete_wet_leaves_by_id(db: Session, wet_leaves_id: int):
    wet_leaves = db.query(models.WetLeaves).filter(models.WetLeaves.WetLeavesID == wet_leaves_id).first()
    if wet_leaves:
        db.delete(wet_leaves)
        db.commit()
        return True
    return False

def update_wet_leaves(db: Session, wet_leaves_id: int, wet_leaves_update: schemas.WetLeavesUpdate):
    db_wet_leaves = db.query(models.WetLeaves).filter(models.WetLeaves.WetLeavesID == wet_leaves_id).first()
    if not db_wet_leaves:
        return None
    db_wet_leaves.Weight = wet_leaves_update.Weight
    if wet_leaves_update.Expiration is not None:
        db_wet_leaves.Expiration = wet_leaves_update.Expiration
    db.commit()
    db.refresh(db_wet_leaves)
    return db_wet_leaves

def update_wet_leaves_status(db: Session, wet_leaves_id: int, status_update: schemas.WetLeavesStatusUpdate):
    db_wet_leaves = db.query(models.WetLeaves).filter(models.WetLeaves.WetLeavesID == wet_leaves_id).first()
    if not db_wet_leaves:
        return None
    db_wet_leaves.Status = status_update.Status
    db.commit()
    db.refresh(db_wet_leaves)
    return db_wet_leaves

# dry leaves
def create_dry_leaves(db: Session, dry_leaves: schemas.DryLeavesCreate):
    # Validate the wet leaves ID
    wet_leaves = get_wet_leaves_by_user_and_id(db, dry_leaves.UserID, dry_leaves.WetLeavesID)
    
    if not wet_leaves:
        raise HTTPException(status_code=404, detail="Wet leaves not found or do not belong to the user")

    db_dry_leaves = models.DryLeaves(**dry_leaves.dict())
    db.add(db_dry_leaves)
    db.commit()
    db.refresh(db_dry_leaves)
    return db_dry_leaves

def get_dry_leaves(db: Session):
    results = (
        db.query(
            models.DryLeaves.DryLeavesID,
            models.DryLeaves.WetLeavesID,
            models.DryLeaves.Processed_Weight,
            models.DryLeaves.Expiration,
            models.DryLeaves.Status,
            models.User.Username  # Include Username from User table
        )
        .join(models.User, models.DryLeaves.UserID == models.User.UserID)
        .all()
    )

    # Convert results into dictionaries
    return [dict(row._mapping) for row in results]


def get_dry_leaves_by_id(db: Session, dry_leaves_id: int):
    return db.query(models.DryLeaves).filter(models.DryLeaves.DryLeavesID == dry_leaves_id).first()

def get_dry_leaves_by_user_id(db: Session, user_id: str):
    return db.query(models.DryLeaves).filter(models.DryLeaves.UserID == user_id).all()

def get_dry_leaves_by_user_and_id(db: Session, user_id: str, dry_leaves_id: int):
    return db.query(models.DryLeaves).filter(models.DryLeaves.UserID == user_id, models.DryLeaves.DryLeavesID == dry_leaves_id).first()

def sum_total_dry_leaves(db: Session):
    total = db.query(func.sum(models.DryLeaves.Processed_Weight)).scalar()
    return int(total or 0)

def sum_get_dry_leaves_by_user_id(db: Session, user_id: str):
    total = (
        db.query(func.sum(models.DryLeaves.Processed_Weight))
        .filter(models.DryLeaves.UserID == user_id)
        .scalar()
    )
    return int(total or 0)


def delete_dry_leaves_by_id(db: Session, dry_leaves_id: int):
    dry_leaves = db.query(models.DryLeaves).filter(models.DryLeaves.DryLeavesID == dry_leaves_id).first()
    if dry_leaves:
        db.delete(dry_leaves)
        db.commit()
        return True
    return False

def update_dry_leaves(db: Session, dry_leaves_id: int, dry_leaves_update: schemas.DryLeavesUpdate):
    db_dry_leaves = db.query(models.DryLeaves).filter(models.DryLeaves.DryLeavesID == dry_leaves_id).first()
    if not db_dry_leaves:
        return None
    db_dry_leaves.Processed_Weight = dry_leaves_update.Weight
    if dry_leaves_update.Expiration is not None:
        db_dry_leaves.Expiration = dry_leaves_update.Expiration
    db.commit()
    db.refresh(db_dry_leaves)
    return db_dry_leaves

def update_dry_leaves_status(db: Session, dry_leaves_id: int, status_update: schemas.DryLeavesStatusUpdate):
    db_dry_leaves = db.query(models.DryLeaves).filter(models.DryLeaves.DryLeavesID == dry_leaves_id).first()
    if not db_dry_leaves:
        return None
    db_dry_leaves.Status = status_update.Status
    db.commit()
    db.refresh(db_dry_leaves)
    return db_dry_leaves

# flour
def create_flour(db: Session, flour: schemas.FlourCreate):
    # Validate the dry leaves ID
    dry_leaves = get_dry_leaves_by_user_and_id(db, flour.UserID, flour.DryLeavesID)
    if not dry_leaves:
        raise HTTPException(status_code=404, detail="Dry leaves not found or do not belong to the user")

    db_flour = models.Flour(**flour.dict())
    db.add(db_flour)
    db.commit()
    db.refresh(db_flour)
    return db_flour
    
def get_flour(db: Session):
    results = (
        db.query(
            models.Flour.FlourID,
            models.Flour.Flour_Weight,
            models.Flour.Expiration,
            models.Flour.Status,
            models.User.Username  # Include Username from User table
        )
        .join(models.User, models.Flour.UserID == models.User.UserID)
        .all()
    )

    # Convert results into dictionaries
    return [dict(row._mapping) for row in results]

def get_flour_by_id(db: Session, flour_id: int):
    return db.query(models.Flour).filter(models.Flour.FlourID == flour_id).first()

def get_flour_by_user_id(db: Session, user_id: str):
    return db.query(models.Flour).filter(models.Flour.UserID == user_id).all()

def sum_total_flour(db: Session):
    total = db.query(func.sum(models.Flour.Flour_Weight)).scalar()
    return int(total or 0)

def sum_get_flour_by_user_id(db: Session, user_id: str):
    total = (
        db.query(func.sum(models.Flour.Flour_Weight))
        .filter(models.Flour.UserID == user_id)
        .scalar()
    )
    return int(total or 0)

def delete_flour_by_id(db: Session, flour_id: int):
    flour = db.query(models.Flour).filter(models.Flour.FlourID == flour_id).first()
    if flour:
        db.delete(flour)
        db.commit()
        return True
    return False

def update_flour(db: Session, flour_id: int, flour_update: schemas.FlourUpdate):
    db_flour = db.query(models.Flour).filter(models.Flour.FlourID == flour_id).first()
    if not db_flour:
        return None
    db_flour.Flour_Weight = flour_update.Weight
    if flour_update.Expiration is not None:
        db_flour.Expiration = flour_update.Expiration
    db.commit()
    db.refresh(db_flour)
    return db_flour

def update_flour_status(db: Session, flour_id: int, status_update: schemas.FlourStatusUpdate):
    db_flour = db.query(models.Flour).filter(models.Flour.FlourID == flour_id).first()
    if not db_flour:
        return None
    db_flour.Status = status_update.Status
    db.commit()
    db.refresh(db_flour)
    return db_flour

# shipment
def create_shipment(db: Session, shipment: schemas.ShipmentCreate):
    db_shipment = models.Shipment(
        CourierID=shipment.CourierID,
        UserID=shipment.UserID,
        ShipmentQuantity=shipment.ShipmentQuantity,
        # ShipmentDate=shipment.ShipmentDate,
        # Check_in_Date=shipment.Check_in_Date,
        # Check_in_Quantity=shipment.Check_in_Quantity,
        # Harbor_Reception_File=shipment.Harbor_Reception_File,
        # Rescalled_Weight=shipment.Rescalled_Weight,
        # Rescalled_Date=shipment.Rescalled_Date,
        # Centra_Reception_File=shipment.Centra_Reception_File,
    )
    db.add(db_shipment)
    db.commit()
    db.refresh(db_shipment)

    for flour_id in shipment.FlourIDs:
        flour = db.query(models.Flour).filter(models.Flour.FlourID == flour_id).first()
        if flour:
            db_shipment.flours.append(flour)
    db.commit()
    db.refresh(db_shipment)

    # Include FlourIDs in the response
    shipment_data = schemas.Shipment(
        ShipmentID=db_shipment.ShipmentID,
        CourierID=db_shipment.CourierID,
        UserID=db_shipment.UserID,
        FlourIDs=[flour.FlourID for flour in db_shipment.flours],
        ShipmentQuantity=db_shipment.ShipmentQuantity,
        # ShipmentDate=db_shipment.ShipmentDate,
        # Check_in_Date=db_shipment.Check_in_Date,
        # Check_in_Quantity=db_shipment.Check_in_Quantity,
        # Harbor_Reception_File=db_shipment.Harbor_Reception_File,
        # Rescalled_Weight=db_shipment.Rescalled_Weight,
        # Rescalled_Date=db_shipment.Rescalled_Date,
        # Centra_Reception_File=db_shipment.Centra_Reception_File,
    )

    return shipment_data

def get_shipment(db: Session, limit: int = 100):
    shipments = db.query(models.Shipment).limit(limit).all()
    shipment_data = []
    for shipment in shipments:
        shipment_dict = {
            "ShipmentID": shipment.ShipmentID,
            "CourierID": shipment.CourierID,
            "UserID": shipment.UserID,
            "FlourIDs": [flour.FlourID for flour in shipment.flours],  # Ensure FlourIDs are included
            "ShipmentQuantity": shipment.ShipmentQuantity,
            "ShipmentDate": shipment.ShipmentDate,
            "Check_in_Date": shipment.Check_in_Date,
            "Check_in_Quantity": shipment.Check_in_Quantity,
            "Rescalled_Weight" : shipment.Rescalled_Weight,
            "Rescalled_Date" : shipment.Rescalled_Date,
            "Harbor_Reception_File": shipment.Harbor_Reception_File,
            "Centra_Reception_File": shipment.Centra_Reception_File,
        }
        shipment_data.append(shipment_dict)
    return shipment_data

def get_shipment_by_id(db: Session, shipment_id: int):
    shipment = db.query(models.Shipment).filter(models.Shipment.ShipmentID == shipment_id).first()
    if not shipment:
        raise HTTPException(status_code=404, detail="Shipment not found")
    
    flour_weight_sum = sum(flour.Flour_Weight for flour in shipment.flours)
    courier = db.query(models.Courier).filter(models.Courier.CourierID == shipment.CourierID).first()
    user = db.query(models.User).filter(models.User.UserID == shipment.UserID).first()
    
    return {
        "ShipmentID": shipment.ShipmentID,
        "CourierID": shipment.CourierID,
        "UserID": shipment.UserID,
        "FlourIDs": [flour.FlourID for flour in shipment.flours],
        "ShipmentQuantity": shipment.ShipmentQuantity,
        "ShipmentDate": shipment.ShipmentDate,
        "Check_in_Date": shipment.Check_in_Date,
        "Check_in_Quantity": shipment.Check_in_Quantity,
        "Rescalled_Weight": shipment.Rescalled_Weight,
        "Rescalled_Date": shipment.Rescalled_Date,
        "Harbor_Reception_File": shipment.Harbor_Reception_File,
        "Centra_Reception_File": shipment.Centra_Reception_File,
        "FlourWeightSum": flour_weight_sum,
        "CourierName": courier.CourierName if courier else None,
        "UserName": user.Username if user else None
    }

def get_all_shipment_ids(db: Session):
    return db.query(models.Shipment).all()

def get_shipment_by_user_id(db: Session, user_id: str):
    shipments = db.query(models.Shipment).filter(models.Shipment.UserID == user_id).all()
    shipment_data = []
    for shipment in shipments:
        shipment_dict = {
            "ShipmentID": shipment.ShipmentID,
            "CourierID": shipment.CourierID,
            "UserID": shipment.UserID,
            "FlourIDs": [flour.FlourID for flour in shipment.flours],
            "ShipmentQuantity": shipment.ShipmentQuantity,
            "ShipmentDate": shipment.ShipmentDate,
            "Check_in_Date": shipment.Check_in_Date,
            "Check_in_Quantity": shipment.Check_in_Quantity,
            "Rescalled_Weight" : shipment.Rescalled_Weight,
            "Rescalled_Date" : shipment.Rescalled_Date
            
        }
        shipment_data.append(shipment_dict)
    return shipment_data

def sum_total_shipment_quantity(db: Session):
    total = db.query(func.sum(models.Shipment.ShipmentQuantity)).scalar()
    return int(total or 0)

def sum_get_shipment_quantity_by_user_id(db: Session, user_id: str):
    total = (
        db.query(func.sum(models.Shipment.ShipmentQuantity))
        .filter(models.Shipment.UserID == user_id)
        .scalar()
    )
    return int(total or 0)

def get_shipment_ids_with_date_but_no_checkin(db: Session) -> List[str]:
    shipments = db.query(models.Shipment.ShipmentID).filter(
        models.Shipment.ShipmentDate.isnot(None),
        models.Shipment.Check_in_Date.is_(None)
    ).all()
    return [shipment[0] for shipment in shipments]  # Extracting the IDs from the tuples

def get_shipment_flour_associations(db: Session):
    return db.query(models.shipment_flour_association).all()

def get_flours_by_shipment_id(db: Session, shipment_id: int):
    return db.query(models.shipment_flour_association).filter(models.shipment_flour_association.c.shipment_id == shipment_id).all()


def delete_shipment_by_id(db: Session, shipment_id: int):
    shipment = db.query(models.Shipment).filter(models.Shipment.ShipmentID == shipment_id).first()
    if shipment:
        db.delete(shipment)
        db.commit()
        return True
    return False

def update_shipment(db: Session, shipment_id: int, shipment_update: schemas.ShipmentUpdate):
    # Query the shipment by its ID
    db_shipment = db.query(models.Shipment).filter(models.Shipment.ShipmentID == shipment_id).first()
    
    if not db_shipment:
        return None
    if shipment_update.CourierID is not None:
        db_shipment.CourierID = shipment_update.CourierID
    if shipment_update.FlourIDs is not None:
        db_shipment.flours = []
        for flour_id in shipment_update.FlourIDs:
            flour = db.query(models.Flour).filter(models.Flour.FlourID == flour_id).first()
            if flour:
                db_shipment.flours.append(flour)
    if shipment_update.ShipmentQuantity is not None:
        db_shipment.ShipmentQuantity = shipment_update.ShipmentQuantity
    if shipment_update.Check_in_Quantity is not None:
        db_shipment.Check_in_Quantity = shipment_update.Check_in_Quantity
    if shipment_update.Harbor_Reception_File is not None:
        db_shipment.Harbor_Reception_File = shipment_update.Harbor_Reception_File
    if shipment_update.Rescalled_Weight is not None:
        db_shipment.Rescalled_Weight = shipment_update.Rescalled_Weight
    if shipment_update.Centra_Reception_File is not None:
        db_shipment.Centra_Reception_File = shipment_update.Centra_Reception_File

    db.commit()
    db.refresh(db_shipment)
    return db_shipment

def update_shipment_date(db: Session, shipment_id: int, shipment_date_update: schemas.ShipmentDateUpdate):
    db_shipment = db.query(models.Shipment).filter(models.Shipment.ShipmentID == shipment_id).first()
    if not db_shipment:
        return None
    db_shipment.ShipmentDate = shipment_date_update.ShipmentDate
    db.commit()
    db.refresh(db_shipment)

    # Ensure FlourIDs are included in the response
    shipment_data = schemas.Shipment(
        ShipmentID=db_shipment.ShipmentID,
        CourierID=db_shipment.CourierID,
        UserID=db_shipment.UserID,
        FlourIDs=[flour.FlourID for flour in db_shipment.flours],
        ShipmentQuantity=db_shipment.ShipmentQuantity,
        ShipmentDate=db_shipment.ShipmentDate,
    )
    return shipment_data

def update_shipment_check_in(db: Session, shipment_id: int, check_in_update: schemas.ShipmentCheckInUpdate):
    db_shipment = db.query(models.Shipment).filter(models.Shipment.ShipmentID == shipment_id).first()
    if not db_shipment:
        return None
    db_shipment.Check_in_Date = check_in_update.Check_in_Date  # This will set to None if provided
    db_shipment.Check_in_Quantity = check_in_update.Check_in_Quantity  # This will set to None if provided

    db.commit()
    db.refresh(db_shipment)

    # Ensure FlourIDs are included in the response
    shipment_data = schemas.Shipment(
        ShipmentID=db_shipment.ShipmentID,
        CourierID=db_shipment.CourierID,
        UserID=db_shipment.UserID,
        FlourIDs=[flour.FlourID for flour in db_shipment.flours],
        ShipmentQuantity=db_shipment.ShipmentQuantity,
        ShipmentDate=db_shipment.ShipmentDate,
        Check_in_Date=db_shipment.Check_in_Date,
        Check_in_Quantity=db_shipment.Check_in_Quantity,
    )
    return shipment_data

def update_shipment_rescalled_weight_and_date(db: Session, shipment_id: int, update_data: schemas.ShipmentRescalledWeightUpdate):
    db_shipment = db.query(models.Shipment).filter(models.Shipment.ShipmentID == shipment_id).first()
    if not db_shipment:
        return None
    db_shipment.Rescalled_Weight = update_data.Rescalled_Weight  # This will set to None if provided
    db_shipment.Rescalled_Date = update_data.Rescalled_Date  # This will set to None if provided

    db.commit()
    db.refresh(db_shipment)
    return {
        "ShipmentID": db_shipment.ShipmentID,
        "CourierID": db_shipment.CourierID,
        "UserID": db_shipment.UserID,
        "FlourIDs": [flour.FlourID for flour in db_shipment.flours],
        "ShipmentQuantity": db_shipment.ShipmentQuantity,
        "ShipmentDate": db_shipment.ShipmentDate,
        "Check_in_Date": db_shipment.Check_in_Date,
        "Check_in_Quantity": db_shipment.Check_in_Quantity,
        "Rescalled_Weight": db_shipment.Rescalled_Weight,
        "Rescalled_Date": db_shipment.Rescalled_Date,
    }
    

def update_shipment_harbor_reception(db: Session, shipment_id: int, update_data: schemas.ShipmentHarborReceptionUpdate):
    db_shipment = db.query(models.Shipment).filter(models.Shipment.ShipmentID == shipment_id).first()
    if not db_shipment:
        return None
    db_shipment.Harbor_Reception_File = update_data.Harbor_Reception_File
    db.commit()
    db.refresh(db_shipment)

    shipment_data = schemas.Shipment(
        ShipmentID=db_shipment.ShipmentID,
        CourierID=db_shipment.CourierID,
        UserID=db_shipment.UserID,
        FlourIDs=[flour.FlourID for flour in db_shipment.flours],
        ShipmentQuantity=db_shipment.ShipmentQuantity,
        ShipmentDate=db_shipment.ShipmentDate,
        Check_in_Date=db_shipment.Check_in_Date,
        Check_in_Quantity=db_shipment.Check_in_Quantity,
        Rescalled_Weight=db_shipment.Rescalled_Weight,
        Rescalled_Date=db_shipment.Rescalled_Date,
        Harbor_Reception_File=db_shipment.Harbor_Reception_File,
        Centra_Reception_File=db_shipment.Centra_Reception_File,
    )
    return shipment_data

def update_shipment_centra_reception(db: Session, shipment_id: int, update_data: schemas.ShipmentCentraReceptionUpdate):
    db_shipment = db.query(models.Shipment).filter(models.Shipment.ShipmentID == shipment_id).first()
    if not db_shipment:
        return None
    db_shipment.Centra_Reception_File = update_data.Centra_Reception_File
    db.commit()
    db.refresh(db_shipment)
    
    shipment_data = schemas.Shipment(
        ShipmentID=db_shipment.ShipmentID,
        CourierID=db_shipment.CourierID,
        UserID=db_shipment.UserID,
        FlourIDs=[flour.FlourID for flour in db_shipment.flours],
        ShipmentQuantity=db_shipment.ShipmentQuantity,
        ShipmentDate=db_shipment.ShipmentDate,
        Check_in_Date=db_shipment.Check_in_Date,
        Check_in_Quantity=db_shipment.Check_in_Quantity,
        Rescalled_Weight=db_shipment.Rescalled_Weight,
        Rescalled_Date=db_shipment.Rescalled_Date,
        Harbor_Reception_File=db_shipment.Harbor_Reception_File,
        Centra_Reception_File=db_shipment.Centra_Reception_File,
    )
    return shipment_data

# location
def create_location(db: Session, location: schemas.LocationCreate):
    db_location = models.Location(**location.dict())
    db.add(db_location)
    db.commit()
    db.refresh(db_location)
    return db_location
    
def get_location(db: Session, limit: int = 100):
    return db.query(models.Location).limit(limit).all()

def get_location_by_user_id(db: Session, user_id: int):
    return db.query(models.Location).filter(models.Location.user_id == user_id).first()

def patch_location_by_user_id(db: Session, user_id: int, location: schemas.LocationPatch):
    db_location = db.query(models.Location).filter(models.Location.user_id == user_id).first()
    
    db_location.latitude = location.latitude
    db_location.longitude = location.longitude
    db_location.location_address = location.location_address
    
    db.commit()
    db.refresh(db_location)
    return db_location

    
    
# def delete_location_by_id(db: Session, location_id: int):
#     location = db.query(models.Location).filter(models.Location.location_id == location_id).first()
#     if location:
#         db.delete(location)
#         db.commit()
#         return True
#     return False


#marketplace
# admin settings
def create_admin_settings(db: Session, admin_settings: schemas.AdminSettingsCreate):
    db_admin_settings = models.AdminSettings(**admin_settings.dict())
    db.add(db_admin_settings)
    db.commit()
    db.refresh(db_admin_settings)
    return db_admin_settings

def get_admin_settings(db: Session):
    return db.query(models.AdminSettings).first()

def update_admin_settings(db: Session, admin_settings_id: int, admin_settings_update: schemas.AdminSettingsBase):
    admin_settings = db.query(models.AdminSettings).filter(models.AdminSettings.AdminSettingsID == admin_settings_id).first()
    if not admin_settings:
        return None
    admin_settings.AdminFeeValue = admin_settings_update.AdminFeeValue
    db.commit()
    db.refresh(admin_settings)
    return admin_settings

# products
def create_product(db: Session, product: schemas.ProductsCreate):
    db_product = models.Products(**product.dict())
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return db_product

def get_products(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Products).offset(skip).limit(limit).all()

def get_product_by_id(db: Session, product_id: int):
    return db.query(models.Products).filter(models.Products.ProductID == product_id).first()

def update_product(db: Session, product_id: int, product_update: schemas.ProductsBase):
    product = db.query(models.Products).filter(models.Products.ProductID == product_id).first()
    if not product:
        return None
    product.ProductName = product_update.ProductName
    db.commit()
    db.refresh(product)
    return product

def delete_product(db: Session, product_id: int):
    product = db.query(models.Products).filter(models.Products.ProductID == product_id).first()
    if product:
        db.delete(product)
        db.commit()
        return True
    return False

# centra setting detail
def create_centra_setting_detail(db: Session, centra_setting_detail: schemas.CentraSettingDetailCreate):
    db_centra_setting_detail = models.CentraSettingDetail(**centra_setting_detail.dict())
    db.add(db_centra_setting_detail)
    db.commit()
    db.refresh(db_centra_setting_detail)
    return db_centra_setting_detail

def get_centra_setting_details(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.CentraSettingDetail).offset(skip).limit(limit).all()

def get_centra_setting_detail_by_id(db: Session, setting_detail_id: int):
    return db.query(models.CentraSettingDetail).filter(models.CentraSettingDetail.SettingDetailID == setting_detail_id).first()

def get_centra_setting_detail_by_user_id(db: Session, user_id: str):
    return db.query(models.CentraSettingDetail).filter(models.CentraSettingDetail.UserID == user_id).all()

def get_centra_setting_detail_by_user_id_and_item(db: Session, user_id: str, item_name: str):
    return db.query(models.CentraSettingDetail).join(models.Products, models.CentraSettingDetail.ProductID == models.Products.ProductID).filter(and_(
                models.CentraSettingDetail.UserID == user_id,
                models.Products.ProductName == item_name
            )).all()

def update_centra_setting_detail(db: Session, setting_detail_id: int, setting_detail_update: schemas.CentraSettingDetailBase):
    centra_setting_detail = db.query(models.CentraSettingDetail).filter(models.CentraSettingDetail.SettingDetailID == setting_detail_id).first()
    if not centra_setting_detail:
        return None
    centra_setting_detail.UserID = setting_detail_update.UserID
    centra_setting_detail.ProductID = setting_detail_update.ProductID
    centra_setting_detail.DiscountRate = setting_detail_update.DiscountRate  
    centra_setting_detail.ExpDayLeft = setting_detail_update.ExpDayLeft      
    db.commit()
    db.refresh(centra_setting_detail)
    return centra_setting_detail

def patch_centra_setting_detail(
    db: Session, setting_detail_id: int, setting_detail_update: schemas.CentraSettingDetailUpdate
):
    centra_setting_detail = db.query(models.CentraSettingDetail).filter(
        models.CentraSettingDetail.SettingDetailID == setting_detail_id
    ).first()

    if not centra_setting_detail:
        return None

    # Update only the fields that are provided
    if setting_detail_update.DiscountRate is not None:
        centra_setting_detail.DiscountRate = setting_detail_update.DiscountRate

    if setting_detail_update.ExpDayLeft is not None:
        centra_setting_detail.ExpDayLeft = setting_detail_update.ExpDayLeft

    db.commit()
    db.refresh(centra_setting_detail)
    return centra_setting_detail

def delete_centra_setting_detail(db: Session, setting_detail_id: int):
    centra_setting_detail = db.query(models.CentraSettingDetail).filter(models.CentraSettingDetail.SettingDetailID == setting_detail_id).first()
    if centra_setting_detail:
        db.delete(centra_setting_detail)
        db.commit()
        return True
    return False


# centra base settings
def create_centra_base_settings(db: Session, centra_base_settings: schemas.CentraBaseSettingsCreate):
    db_centra_base_settings = models.CentraBaseSettings(**centra_base_settings.dict())
    db.add(db_centra_base_settings)
    db.commit()
    db.refresh(db_centra_base_settings)
    return db_centra_base_settings

def get_centra_base_settings(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.CentraBaseSettings).offset(skip).limit(limit).all()

def update_centra_base_settings(db: Session, settings_id: int, centra_base_settings_update: schemas.CentraBaseSettingsBase):
    centra_base_settings = db.query(models.CentraBaseSettings).filter(models.CentraBaseSettings.SettingsID == settings_id).first()
    if not centra_base_settings:
        return None
    centra_base_settings.InitialPrice = centra_base_settings_update.InitialPrice
    centra_base_settings.Sellable = centra_base_settings_update.Sellable  # Updated to include Sellable
    db.commit()
    db.refresh(centra_base_settings)
    return centra_base_settings

def delete_centra_base_settings(db: Session, settings_id: int):
    centra_base_settings = db.query(models.CentraBaseSettings).filter(models.CentraBaseSettings.SettingsID == settings_id).first()
    if centra_base_settings:
        db.delete(centra_base_settings)
        db.commit()
        return True
    return False

def get_centra_base_settings_by_user_id_and_items(db: Session, user_id: str, item_name: str):
    return db.query(models.CentraBaseSettings).join(models.Products, models.CentraBaseSettings.ProductID == models.Products.ProductID).filter(and_(
                models.CentraBaseSettings.UserID == user_id,
                models.Products.ProductName == item_name
            )).all()


def patch_centra_base_settings(
    db: Session, UserID: str, ProductID: int, setting_detail_update: schemas.CentraBaseSettingUpdate
):
    # Query the CentraBaseSettings for the given UserID and ProductID
    centra_setting_detail = db.query(models.CentraBaseSettings).filter(
        models.CentraBaseSettings.UserID == UserID,
        models.CentraBaseSettings.ProductID == ProductID
    ).first()

    if not centra_setting_detail:
        raise HTTPException(status_code=404, detail="Centra setting detail not found")

    # Update fields only if provided in the request
    if setting_detail_update.InitialPrice is not None:
        centra_setting_detail.InitialPrice = setting_detail_update.InitialPrice

    if setting_detail_update.Sellable is not None:
        centra_setting_detail.Sellable = setting_detail_update.Sellable

    db.commit()  # Commit the changes
    db.refresh(centra_setting_detail)  # Refresh the object after commit to get the updated values
    return centra_setting_detail


# MarketShipment
def create_market_shipment(db: Session, market_shipment: schemas.MarketShipmentCreate):
    # Convert UUIDs to strings before querying
    centra_id_str = str(market_shipment.CentraID)
    customer_id_str = str(market_shipment.CustomerID)

    # Validate that the CentraID user has the "Centra" role
    centra_user = db.query(models.User).filter(models.User.UserID == centra_id_str).first()
    if not centra_user or centra_user.RoleID != 1:  # Assuming RoleID 1 is for "Centra"
        raise HTTPException(status_code=400, detail="CentraID must reference a user with the 'Centra' role.")

    # Validate that the CustomerID user has the "Customer" role
    customer_user = db.query(models.User).filter(models.User.UserID == customer_id_str).first()
    if not customer_user or customer_user.RoleID != 5:  # Assuming RoleID 5 is for "Customer"
        raise HTTPException(status_code=400, detail="CustomerID must reference a user with the 'Customer' role.")

    db_market_shipment = models.MarketShipment(
        CentraID=market_shipment.CentraID,
        CustomerID=market_shipment.CustomerID,
        DryLeavesID=market_shipment.DryLeavesID,
        PowderID=market_shipment.PowderID,
        status=market_shipment.status
    )
    db.add(db_market_shipment)
    db.commit()
    db.refresh(db_market_shipment)
    return db_market_shipment


def get_market_shipments(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.MarketShipment).offset(skip).limit(limit).all()

def get_market_shipment_by_id(db: Session, market_shipment_id: int):
    return db.query(models.MarketShipment).filter(models.MarketShipment.MarketShipmentID == market_shipment_id).first()

def update_market_shipment(db: Session, market_shipment_id: int, market_shipment_update: schemas.MarketShipmentUpdate):
    db_market_shipment = db.query(models.MarketShipment).filter(models.MarketShipment.MarketShipmentID == market_shipment_id).first()
    if not db_market_shipment:
        return None

    # Validate if CentraID is being updated
    if market_shipment_update.CentraID is not None:
        centra_user = db.query(models.User).filter(models.User.UserID == market_shipment_update.CentraID).first()
        if not centra_user or centra_user.RoleID != 1:  # Assuming RoleID 1 is for "Centra"
            raise HTTPException(status_code=400, detail="CentraID must reference a user with the 'Centra' role.")
        db_market_shipment.CentraID = market_shipment_update.CentraID

    # Validate if CustomerID is being updated
    if market_shipment_update.CustomerID is not None:
        customer_user = db.query(models.User).filter(models.User.UserID == market_shipment_update.CustomerID).first()
        if not customer_user or customer_user.RoleID != 5:  # Assuming RoleID 5 is for "Customer"
            raise HTTPException(status_code=400, detail="CustomerID must reference a user with the 'Customer' role.")
        db_market_shipment.CustomerID = market_shipment_update.CustomerID

    if market_shipment_update.DryLeavesID is not None:
        db_market_shipment.DryLeavesID = market_shipment_update.DryLeavesID
    if market_shipment_update.PowderID is not None:
        db_market_shipment.PowderID = market_shipment_update.PowderID
    if market_shipment_update.status is not None:
        db_market_shipment.status = market_shipment_update.status

    db.commit()
    db.refresh(db_market_shipment)
    return db_market_shipment

def delete_market_shipment(db: Session, market_shipment_id: int):
    db_market_shipment = db.query(models.MarketShipment).filter(models.MarketShipment.MarketShipmentID == market_shipment_id).first()
    if db_market_shipment:
        db.delete(db_market_shipment)
        db.commit()
        return True
    return False

# Transaction
# SubTransaction
def create_subtransaction(db: Session, subtransaction: schemas.SubTransactionCreate):
    db_subtransaction = models.SubTransaction(
        MarketShipmentID=subtransaction.MarketShipmentID,
        status=subtransaction.status
    )
    db.add(db_subtransaction)
    db.commit()
    db.refresh(db_subtransaction)
    return db_subtransaction

def get_subtransactions(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.SubTransaction).offset(skip).limit(limit).all()

def get_subtransaction_by_id(db: Session, subtransaction_id: int):
    return db.query(models.SubTransaction).filter(models.SubTransaction.SubTransactionID == subtransaction_id).first()

def update_subtransaction(db: Session, subtransaction_id: int, subtransaction_update: schemas.SubTransactionUpdate):
    db_subtransaction = db.query(models.SubTransaction).filter(models.SubTransaction.SubTransactionID == subtransaction_id).first()
    if not db_subtransaction:
        return None
    if subtransaction_update.MarketShipmentID is not None:
        db_subtransaction.MarketShipmentID = subtransaction_update.MarketShipmentID
    if subtransaction_update.status is not None:
        db_subtransaction.status = subtransaction_update.status
    db.commit()
    db.refresh(db_subtransaction)
    return db_subtransaction

def delete_subtransaction(db: Session, subtransaction_id: int):
    db_subtransaction = db.query(models.SubTransaction).filter(models.SubTransaction.SubTransactionID == subtransaction_id).first()
    if db_subtransaction:
        db.delete(db_subtransaction)
        db.commit()
        return True
    return False


# Transaction
def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(
        SubTransactionID=transaction.SubTransactionID,
        status=transaction.status
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def get_transactions(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Transaction).offset(skip).limit(limit).all()

def get_transaction_by_id(db: Session, transaction_id: int):
    return db.query(models.Transaction).filter(models.Transaction.TransactionID == transaction_id).first()

def update_transaction(db: Session, transaction_id: int, transaction_update: schemas.TransactionUpdate):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.TransactionID == transaction_id).first()
    if not db_transaction:
        return None
    if transaction_update.SubTransactionID is not None:
        db_transaction.SubTransactionID = transaction_update.SubTransactionID
    if transaction_update.status is not None:
        db_transaction.status = transaction_update.status
    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: int):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.TransactionID == transaction_id).first()
    if db_transaction:
        db.delete(db_transaction)
        db.commit()
        return True
    return False

# centra finance
def create_centra_finance(db: Session, centra_finance: schemas.CentraFinanceCreate):
    db_centra_finance = models.CentraFinance(**centra_finance.dict())
    db.add(db_centra_finance)
    db.commit()
    db.refresh(db_centra_finance)
    return db_centra_finance

def get_centra_finances(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.CentraFinance).offset(skip).limit(limit).all()

def get_centra_finance_by_id(db: Session, finance_id: int):
    return db.query(models.CentraFinance).filter(models.CentraFinance.FinanceID == finance_id).first()

def get_centra_finance_by_userid(db: Session, UserID: str):
    return db.query(models.CentraFinance).filter(models.CentraFinance.UserID == UserID).first()

def update_centra_finance(db: Session, finance_id: int, centra_finance_update: schemas.CentraFinanceBase):
    centra_finance = db.query(models.CentraFinance).filter(models.CentraFinance.FinanceID == finance_id).first()
    if not centra_finance:
        return None
    centra_finance.AccountHolderName = centra_finance_update.AccountHolderName
    centra_finance.BankCode = centra_finance_update.BankCode
    centra_finance.BankAccountNumber = centra_finance_update.BankAccountNumber
    db.commit()
    db.refresh(centra_finance)
    return centra_finance

def delete_centra_finance(db: Session, finance_id: int):
    centra_finance = db.query(models.CentraFinance).filter(models.CentraFinance.FinanceID == finance_id).first()
    if centra_finance:
        db.delete(centra_finance)
        db.commit()
        return True
    return False

def get_random_items(db: Session, item_type: str, limit: int = 100):
    chosen_item = ''
    # Fetch data based on item type
    if item_type.lower() == 'flour':
        items = db.query(models.Flour).order_by(func.random()).limit(limit).all()
        chosen_item = "Powder"
    elif item_type.lower() == 'dry_leaves':
        items = db.query(models.DryLeaves).order_by(func.random()).limit(limit).all()
        chosen_item = "Dry Leaves"
    else:
        raise ValueError("Invalid item type. Choose 'flour' or 'dry_leaves'.")

    # Initialize the dictionary to group items by username
    grouped_data = {}

    currentDate = datetime.now()
    
    # Iterate through each item to populate grouped_data
    for item in items:
        user_id = item.UserID  # Assuming each item has a 'UserID' attribute
        user = get_user_by_id(db, user_id)
                    
        expdayleft = (item.Expiration - currentDate).days
                    
        centra_base_settings = get_centra_base_settings_by_user_id_and_items(db, user_id, "Dry Leaves" if item_type=="dry_leaves" else "Powder")
        discount_conditions = get_centra_setting_detail_by_user_id_and_item(db, user_id, chosen_item)
        
        if not user:
            continue

        username = user.Username
        price = centra_base_settings[0].InitialPrice
        def calculate_discounted_price(expiry_left, data, initial_price):
            # Filter discounts where expiry_left <= expiry
            applicable_discounts = [item for item in data if expiry_left <= item.ExpDayLeft]
            
            if not applicable_discounts:
                # No discounts apply, return the initial price
                return initial_price, False
                       
            # Find the discount with the smallest expiry value
            best_discount = min(applicable_discounts, key=lambda x: x.ExpDayLeft).DiscountRate
            
            # Calculate the discounted price
            discount_amount = (initial_price * best_discount) / 100
            discounted_price = initial_price - discount_amount
           
            return round(discounted_price), True  # Round to the nearest integer

        final_price, discounted = calculate_discounted_price(expdayleft, discount_conditions, price)

        # Check item type to determine structure
        if item_type.lower() == 'dry_leaves':
            item_data = {"id": item.DryLeavesID, "weight": item.Processed_Weight, "initial_price": price, "price": final_price, "discounted": discounted}
        elif item_type.lower() == 'flour':
            item_data = {"id": item.FlourID, "weight": item.Flour_Weight, "initial_price": price, "price": final_price, "discounted": discounted}
       
        # Group by username
        if username not in grouped_data:
            grouped_data[username] = [item_data]
        else:
            grouped_data[username].append(item_data)

    return grouped_data

def get_items(db: Session, item_type: str, limit: int = 100):
    # Fetch data based on item type
    if item_type.lower() == 'flour':
        items = db.query(models.Flour).limit(limit).all()
    elif item_type.lower() == 'dry_leaves':
        items = db.query(models.DryLeaves).limit(limit).all()
    else:
        raise ValueError("Invalid item type. Choose 'flour' or 'dry_leaves'.")

    # Initialize the dictionary to group items by username
    grouped_data = {}

    # Iterate through each item to populate grouped_data
    for item in items:
        user_id = item.UserID  # Assuming each item has a 'UserID' attribute
        user = get_user_by_id(db, user_id)
        if not user:
            continue

        username = user.Username

        # Check item type to determine structure
        if item_type.lower() == 'dry_leaves':
            item_data = {"id": item.DryLeavesID, "weight": item.Processed_Weight}
        elif item_type.lower() == 'flour':
            item_data = {"id": item.FlourID, "weight": item.Flour_Weight}
       
        # Group by username
        if username not in grouped_data:
            grouped_data[username] = [item_data]
        else:
            grouped_data[username].append(item_data)

    return grouped_data

def get_items_by_selected_centra(db: Session, item_type: str, users: List[UUID]):
    # Convert UUIDs to strings to match the VARCHAR column type
    user_ids = [str(user_id) for user_id in users]
    if item_type.lower() == 'flour':
        items = db.query(models.Flour).order_by(func.random()).filter(models.Flour.UserID.in_(user_ids)).all()
    elif item_type.lower() == 'dry_leaves':
        items = db.query(models.DryLeaves).order_by(func.random()).filter(models.DryLeaves.UserID.in_(user_ids)).all()
    else:
        raise ValueError("Invalid item type. Choose 'flour' or 'dry_leaves'.")

    grouped_data = {}

    for item in items:
        user_id = item.UserID
        user = get_user_by_id(db, user_id)
        if not user:
            continue

        username = user.Username
        item_data = {"id": item.DryLeavesID if item_type == 'dry_leaves' else item.FlourID,
                     "weight": item.Processed_Weight if item_type == 'dry_leaves' else item.Flour_Weight}
        
        if username not in grouped_data:
            grouped_data[username] = [item_data]
        else:
            grouped_data[username].append(item_data)

    return grouped_data

def get_random_centras(db: Session, numOfCentra: int):
    return db.query(models.User).filter(models.User.RoleID == 1).order_by(func.random()).limit(numOfCentra).all()

def get_random_items_by_centra(db: Session, item_type: str, numOfCentra: int):
    centraList = get_random_centras(db, numOfCentra)
    # Fetch data based on item type
    if item_type.lower() == 'flour':
        # Fetch flour items filtered by UserID from the selected centra
        items = db.query(models.Flour).filter(models.Flour.UserID.in_([centra.UserID for centra in centraList])).order_by(func.random()).all()
    elif item_type.lower() == 'dry_leaves':
        # Fetch dry leaves items filtered by UserID from the selected centra
        items = db.query(models.DryLeaves).filter(models.DryLeaves.UserID.in_([centra.UserID for centra in centraList])).order_by(func.random()).all()
    else:
        raise ValueError("Invalid item type. Choose 'flour' or 'dry_leaves'.")

    # Initialize the dictionary to group items by username
    grouped_data = {}

    # Iterate through each item to populate grouped_data
    for item in items:
        user_id = item.UserID  # Assuming each item has a 'UserID' attribute
        user = get_user_by_id(db, user_id)
        if not user:
            continue

        username = user.Username

        # Check item type to determine structure
        if item_type.lower() == 'dry_leaves':
            item_data = {"id": item.DryLeavesID, "weight": item.Processed_Weight}
        elif item_type.lower() == 'flour':
            item_data = {"id": item.FlourID, "weight": item.Flour_Weight}
       
        # Group by username
        if username not in grouped_data:
            grouped_data[username] = [item_data]
        else:
            grouped_data[username].append(item_data)

    return grouped_data

def get_random_items_by_centra(db: Session, item_type: str, numOfCentra: int):
    centraList = get_random_centras(db, numOfCentra)
    # Fetch data based on item type
    if item_type.lower() == 'flour':
        # Fetch flour items filtered by UserID from the selected centra
        items = db.query(models.Flour).filter(models.Flour.UserID.in_([centra.UserID for centra in centraList])).order_by(func.random()).all()
    elif item_type.lower() == 'dry_leaves':
        # Fetch dry leaves items filtered by UserID from the selected centra
        items = db.query(models.DryLeaves).filter(models.DryLeaves.UserID.in_([centra.UserID for centra in centraList])).order_by(func.random()).all()
    else:
        raise ValueError("Invalid item type. Choose 'flour' or 'dry_leaves'.")

    # Initialize the dictionary to group items by username
    grouped_data = {}

    # Iterate through each item to populate grouped_data
    for item in items:
        user_id = item.UserID  # Assuming each item has a 'UserID' attribute
        user = get_user_by_id(db, user_id)
        if not user:
            continue

        username = user.Username

        # Check item type to determine structure
        if item_type.lower() == 'dry_leaves':
            item_data = {"id": item.DryLeavesID, "weight": item.Processed_Weight}
        elif item_type.lower() == 'flour':
            item_data = {"id": item.FlourID, "weight": item.Flour_Weight}
       
        # Group by username
        if username not in grouped_data:
            grouped_data[username] = [item_data]
        else:
            grouped_data[username].append(item_data)

    return grouped_data

def get_all_items(db: Session, item_type: str):
    # Fetch data based on item type
    if item_type.lower() == 'flour':
        items = db.query(models.Flour).all()
    elif item_type.lower() == 'dry_leaves':
        items = db.query(models.DryLeaves).all()
    else:
        raise ValueError("Invalid item type. Choose 'flour' or 'dry_leaves'.")

    # Initialize the dictionary to group items by username
    grouped_data = {}

    # Iterate through each item to populate grouped_data
    for item in items:
        user_id = item.UserID  # Assuming each item has a 'UserID' attribute
        user = get_user_by_id(db, user_id)
        if not user:
            continue

        username = user.Username

        # Check item type to determine structure
        if item_type.lower() == 'dry_leaves':
            item_data = {"id": item.DryLeavesID, "weight": item.Processed_Weight}
        elif item_type.lower() == 'flour':
            item_data = {"id": item.FlourID, "weight": item.Flour_Weight}
       
        # Group by username
        if username not in grouped_data:
            grouped_data[username] = [item_data]
        else:
            grouped_data[username].append(item_data)

    return grouped_data

def bulk_algorithm_by_random_centras(db: Session, item_type: str, target_weight: int):
    all_data = get_random_items_by_centra(db, item_type, round(target_weight/1000))
    
    memo: dict[tuple[int, int], int] = {}
    next: dict[tuple[int, int], tuple[int, int, bool]] = {}

    def dp(weight: int, idx: int, items: list[tuple[int, str, int]]) -> int:
        if memo.get((weight, idx), -1) != -1:
            return memo.get((weight, idx))
        if weight <= 0 or idx >= len(items):
            return 0

        # Decision to include the current item
        if weight - items[idx][0] >= 0:
            next[(weight, idx)] = (weight - items[idx][0], idx + 1, True)
            memo[(weight, idx)] = dp(weight - items[idx][0], idx + 1, items=items) + items[idx][0]

        # Decision to skip the current item
        skip_value = dp(weight, idx + 1, items=items)
        if memo.get((weight, idx), 0) < skip_value:
            next[(weight, idx)] = (weight, idx + 1, False)
            memo[(weight, idx)] = skip_value

        return memo.get((weight, idx), 0)

    def knapsack(target_weight: int, item_weights: dict[str, list[dict[str, int]]]):
        items: list[tuple[int, str, int]] = []
        memo.clear()
        next.clear()
        
        # Flatten input structure into list of (weight, category, id) tuples
        for category, weights in item_weights.items():
            items += [(item["weight"], category, item["id"]) for item in weights]

        max_value = dp(target_weight, 0, items)
        
        # Build choices in the same structure as input
        choices: dict[str, list[dict[str, int]]] = {}
        current = (target_weight, 0)

        while next.get(current):
            weight, category, item_id = items[current[1]]
            if next[current][2]:  # If the item was included in the optimal solution
                if category not in choices:
                    choices[category] = []
                choices[category].append({"id": item_id, "weight": weight})
            current = next[current][:2]
        
        return max_value, choices
    
    max_value, choices = knapsack(target_weight, all_data)
    
    return max_value, choices


def bulk_algorithm_by_random_items(db: Session, item_type: str, target_weight: int):
    all_data = get_random_items(db, item_type, round(target_weight / 25))
    
    memo: dict[tuple[int, int], int] = {}
    next: dict[tuple[int, int], tuple[int, int, bool]] = {}

    def dp(weight: int, idx: int, items: list[tuple[int, str, int, int]]) -> int:
        if memo.get((weight, idx), -1) != -1:
            return memo.get((weight, idx))
        if weight <= 0 or idx >= len(items):
            return 0

        # Decision to include the current item
        if weight - items[idx][0] >= 0:
            next[(weight, idx)] = (weight - items[idx][0], idx + 1, True)
            memo[(weight, idx)] = dp(weight - items[idx][0], idx + 1, items=items) + items[idx][0]

        # Decision to skip the current item
        skip_value = dp(weight, idx + 1, items=items)
        if memo.get((weight, idx), 0) < skip_value:
            next[(weight, idx)] = (weight, idx + 1, False)
            memo[(weight, idx)] = skip_value

        return memo.get((weight, idx), 0)

    def knapsack(target_weight: int, item_weights: dict[str, list[dict[str, int]]]):
        items: list[tuple[int, str, int, int, bool, int]] = []  # Add `initial_price` to tuple
        memo.clear()
        next.clear()

        for category, weights in item_weights.items():
            items += [
                (
                    item.get("weight", 0),
                    category,
                    item.get("id", 0),
                    item.get("price", 0),
                    item.get("discounted", False),
                    item.get("initial_price", 0),  # Add `initial_price`
                )
                for item in weights
            ]

        max_value = dp(target_weight, 0, items)

        choices: dict[str, list[dict[str, int]]] = {}
        current = (target_weight, 0)

        while current in next:
            weight, category, item_id, price, discounted, initial_price = items[current[1]]
            if next[current][2]:
                if category not in choices:
                    choices[category] = []
                choices[category].append({
                    "id": item_id,
                    "weight": weight,
                    "price": price,
                    "discounted": discounted,
                    "initial_price": initial_price,  # Include `initial_price`
                })
            current = next[current][:2]

        return max_value, choices

    max_value, choices = knapsack(target_weight, all_data)
    
    return max_value, choices


def bulk_algorithm_by_selected_centra(db: Session, item_type: str, target_weight: int, users: List[UUID]):
    all_data = get_items_by_selected_centra(db, item_type, users)
    
    memo: dict[tuple[int, int], int] = {}
    next_choice: dict[tuple[int, int], tuple[int, int, bool]] = {}

    def dp(weight: int, idx: int, items: list[tuple[int, str, int]]) -> int:
        if (weight, idx) in memo:
            return memo[(weight, idx)]
        if weight <= 0 or idx >= len(items):
            return 0

        include_value = 0
        if weight - items[idx][0] >= 0:
            include_value = dp(weight - items[idx][0], idx + 1, items) + items[idx][0]
            next_choice[(weight, idx)] = (weight - items[idx][0], idx + 1, True)
        
        skip_value = dp(weight, idx + 1, items)
        if skip_value > include_value:
            next_choice[(weight, idx)] = (weight, idx + 1, False)

        memo[(weight, idx)] = max(include_value, skip_value)
        return memo[(weight, idx)]

    def knapsack(target_weight: int, item_weights: dict[str, list[dict[str, int]]]):
        items: list[tuple[int, str, int]] = []
        memo.clear()
        next_choice.clear()
        
        for category, weights in item_weights.items():
            items += [(item["weight"], category, item["id"]) for item in weights]

        max_value = dp(target_weight, 0, items)
        
        choices: dict[str, list[dict[str, int]]] = {}
        current = (target_weight, 0)

        while next_choice.get(current):
            weight, category, item_id = items[current[1]]
            if next_choice[current][2]:
                if category not in choices:
                    choices[category] = []
                choices[category].append({"id": item_id, "weight": weight})
            current = next_choice[current][:2]
        
        return max_value, choices
    
    max_value, choices = knapsack(target_weight, all_data)
    
    return max_value, choices

