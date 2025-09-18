import bcrypt
from sqlalchemy import cast, Date, and_, text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Session
from datetime import datetime, timedelta    
from fastapi import HTTPException, Depends
from sqlalchemy.sql import func
from typing import List, Optional
import models
import schemas
import uuid
from sqlalchemy.orm import aliased, joinedload, selectinload
from sqlalchemy import union_all, select, literal_column

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

def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.Username == username).first()


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

def create_market_shipment(db: Session, market_shipment: schemas.MarketShipmentCreate, session_data: schemas.SessionData):
    centra_id_str = str(market_shipment.CentraID)
    customer_id_str = str(session_data.UserID)

    # Validate Centra user
    centra_user = db.query(models.User).filter(models.User.UserID == centra_id_str).first()
    if not centra_user or centra_user.RoleID != 1:
        raise HTTPException(status_code=400, detail="CentraID must reference a user with the 'Centra' role.")

    # Validate Customer user
    customer_user = db.query(models.User).filter(models.User.UserID == customer_id_str).first()
    if not customer_user or customer_user.RoleID != 5:
        raise HTTPException(status_code=400, detail="CustomerID must reference a user with the 'Customer' role.")

    # Step 1: Create Transaction
    transaction_id = str(uuid.uuid4())
    db_transaction = models.Transaction(
        TransactionID=transaction_id,
        CustomerID = customer_id_str
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)

    # Step 2: Create SubTransaction linked to the Transaction
    db_sub_transaction = models.SubTransaction(
        TransactionID=transaction_id,
        CentraID=market_shipment.CentraID  # Moved CentraID to SubTransaction
    )
    db.add(db_sub_transaction)
    db.commit()
    db.refresh(db_sub_transaction)

    # Step 3: Create MarketShipment linked to the SubTransaction
    db_market_shipment = models.MarketShipment(
        SubTransactionID=db_sub_transaction.SubTransactionID,
        ProductTypeID=market_shipment.ProductTypeID,
        ProductID=market_shipment.ProductID,
        Price=market_shipment.Price,
        InitialPrice=market_shipment.InitialPrice,
    )
    db.add(db_market_shipment)
    db.commit()
    db.refresh(db_market_shipment)

    return {
        "TransactionID": transaction_id
    }



def get_market_shipments(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.MarketShipment).offset(skip).limit(limit).all()

def get_market_shipment_by_id(db: Session, market_shipment_id: int):
    return db.query(models.MarketShipment).filter(models.MarketShipment.MarketShipmentID == market_shipment_id).first()

def create_subtransaction(db: Session, subtransaction: schemas.SubTransactionCreate):
    db_subtransaction = models.SubTransaction(
        TransactionID=subtransaction.TransactionID,  # Reference Transaction
        CentraID=subtransaction.CentraID,  # Move CentraID to SubTransaction
        SubTransactionStatus=subtransaction.status
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
    if subtransaction_update.CentraID is not None:
        db_subtransaction.CentraID = subtransaction_update.CentraID  # Update CentraID here
    if subtransaction_update.status is not None:
        db_subtransaction.SubTransactionStatus = subtransaction_update.status
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

# --- Create Transaction ---
def create_transaction(db: Session, transaction: schemas.TransactionCreate):
    db_transaction = models.Transaction(
        TransactionID=str(uuid.uuid4()),
        CustomerID=str(transaction.CustomerID),
        TransactionStatus=transaction.status or "pending"
    )
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction


def create_single_transaction_by_customer(db: Session, market_shipment: schemas.MarketShipmentCreate, session_data: schemas.SessionData):
    centra_id_str = str(market_shipment.CentraID)
    customer_id_str = str(session_data.UserID)

    # Validate Centra user
    centra_user = db.query(models.User).filter(models.User.UserID == centra_id_str).first()
    if not centra_user or centra_user.RoleID != 1:
        raise HTTPException(status_code=400, detail="CentraID must reference a user with the 'Centra' role.")

    # Validate Customer user
    customer_user = db.query(models.User).filter(models.User.UserID == customer_id_str).first()
    if not customer_user or customer_user.RoleID != 5:
        raise HTTPException(status_code=400, detail="CustomerID must reference a user with the 'Customer' role.")

    # Database transaction with row-level locking
    try:
        # Lock the specific product row to prevent concurrent modifications
        product_table = None
        product_query = None
        
        if market_shipment.ProductTypeID == 1:  # Wet Leaves
            product_table = models.WetLeaves
            product_query = db.query(models.WetLeaves).filter(
                models.WetLeaves.WetLeavesID == market_shipment.ProductID
            ).with_for_update(nowait=False)
        elif market_shipment.ProductTypeID == 2:  # Dry Leaves
            product_table = models.DryLeaves
            product_query = db.query(models.DryLeaves).filter(
                models.DryLeaves.DryLeavesID == market_shipment.ProductID
            ).with_for_update(nowait=False)
        elif market_shipment.ProductTypeID == 3:  # Flour
            product_table = models.Flour
            product_query = db.query(models.Flour).filter(
                models.Flour.FlourID == market_shipment.ProductID
            ).with_for_update(nowait=False)
        else:
            raise HTTPException(status_code=400, detail="Invalid ProductTypeID")

        # Lock and validate the product exists and is available
        locked_product = product_query.first()
        if not locked_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if product is available (not already processed or sold)
        if hasattr(locked_product, 'Status') and locked_product.Status in ['Processed', 'Sold', 'Expired']:
            raise HTTPException(status_code=400, detail=f"Product is not available. Current status: {locked_product.Status}")

        # Check product ownership belongs to the centra
        if locked_product.UserID != centra_id_str:
            raise HTTPException(status_code=403, detail="Product does not belong to the specified centra")

        # Step 1: Create Transaction with default status
        transaction_id = str(uuid.uuid4())
        db_transaction = models.Transaction(
            TransactionID=transaction_id,
            CustomerID = customer_id_str,
            TransactionStatus="Transaction Pending"  # Default status
        )
        db.add(db_transaction)
        db.flush()  # Use flush instead of commit to keep transaction open

        # Step 2: Create SubTransaction linked to the Transaction
        db_sub_transaction = models.SubTransaction(
            TransactionID=transaction_id,
            CentraID=market_shipment.CentraID  # Moved CentraID to SubTransaction
        )
        db.add(db_sub_transaction)
        db.flush()

        # Step 3: Create MarketShipment linked to the SubTransaction
        db_market_shipment = models.MarketShipment(
            SubTransactionID=db_sub_transaction.SubTransactionID,
            ProductTypeID=market_shipment.ProductTypeID,
            ProductID=market_shipment.ProductID,
            Price=market_shipment.Price,
            InitialPrice=market_shipment.InitialPrice,
        )
        db.add(db_market_shipment)
        db.flush()

        # Update product status to "Reserved" to indicate it's part of a transaction
        locked_product.Status = "Reserved"
        db.flush()

        # Commit the entire transaction
        db.commit()
        
        return {
            "TransactionID": transaction_id,
            "message": "Transaction created successfully with product locked"
        }

    except Exception as e:
        # Rollback on any error
        db.rollback()
        if "could not obtain lock" in str(e).lower():
            raise HTTPException(status_code=423, detail="Product is currently being processed by another transaction. Please try again.")
        raise e


def create_bulk_transaction_by_customer(db: Session, bulk_transaction: schemas.BulkTransactionCreate, session_data: schemas.SessionData):
    """Create a bulk transaction with multiple items, with row-level locking and proper error handling"""
    customer_id_str = str(session_data.UserID)
    
    # Validate Customer user
    customer_user = db.query(models.User).filter(models.User.UserID == customer_id_str).first()
    if not customer_user or customer_user.RoleID != 5:
        raise HTTPException(status_code=400, detail="CustomerID must reference a user with the 'Customer' role.")

    if not bulk_transaction.items:
        raise HTTPException(status_code=400, detail="Bulk transaction must contain at least one item")

    failed_items = []
    successful_items = []
    
    # Create the main transaction first with default status
    transaction_id = str(uuid.uuid4())
    db_transaction = models.Transaction(
        TransactionID=transaction_id,
        CustomerID=customer_id_str,
        TransactionStatus="Transaction Pending"  # Default status
    )
    
    try:
        db.add(db_transaction)
        db.flush()  # Create transaction but keep it open
        
        # Group items by centra to create sub-transactions
        centra_groups = {}
        for item in bulk_transaction.items:
            centra_id = str(item.CentraID)
            if centra_id not in centra_groups:
                centra_groups[centra_id] = []
            centra_groups[centra_id].append(item)
        
        # Process each centra group
        for centra_id, items in centra_groups.items():
            # Validate Centra user
            centra_user = db.query(models.User).filter(models.User.UserID == centra_id).first()
            if not centra_user or centra_user.RoleID != 1:
                failed_items.extend([{
                    "item": item.dict(),
                    "error": f"CentraID {centra_id} must reference a user with the 'Centra' role."
                } for item in items])
                continue
            
            # Create sub-transaction for this centra
            db_sub_transaction = models.SubTransaction(
                TransactionID=transaction_id,
                CentraID=centra_id,
                SubTransactionStatus="pending"
            )
            db.add(db_sub_transaction)
            db.flush()
            
            # Process each item for this centra
            for item in items:
                try:
                    # Lock the specific product row to prevent concurrent modifications
                    product_table = None
                    product_query = None
                    
                    if item.ProductTypeID == 1:  # Wet Leaves
                        product_table = models.WetLeaves
                        product_query = db.query(models.WetLeaves).filter(
                            models.WetLeaves.WetLeavesID == item.ProductID
                        ).with_for_update(nowait=False)
                    elif item.ProductTypeID == 2:  # Dry Leaves
                        product_table = models.DryLeaves
                        product_query = db.query(models.DryLeaves).filter(
                            models.DryLeaves.DryLeavesID == item.ProductID
                        ).with_for_update(nowait=False)
                    elif item.ProductTypeID == 3:  # Flour
                        product_table = models.Flour
                        product_query = db.query(models.Flour).filter(
                            models.Flour.FlourID == item.ProductID
                        ).with_for_update(nowait=False)
                    else:
                        failed_items.append({
                            "item": item.dict(),
                            "error": "Invalid ProductTypeID"
                        })
                        continue

                    # Lock and validate the product exists and is available
                    locked_product = product_query.first()
                    if not locked_product:
                        failed_items.append({
                            "item": item.dict(),
                            "error": "Product not found"
                        })
                        continue
                    
                    # Check if product is available (not already processed or sold)
                    if hasattr(locked_product, 'Status') and locked_product.Status in ['Processed', 'Sold', 'Expired']:
                        failed_items.append({
                            "item": item.dict(),
                            "error": f"Product is not available. Current status: {locked_product.Status}"
                        })
                        continue

                    # Check product ownership belongs to the centra
                    if locked_product.UserID != centra_id:
                        failed_items.append({
                            "item": item.dict(),
                            "error": "Product does not belong to the specified centra"
                        })
                        continue

                    # Create MarketShipment for this item
                    db_market_shipment = models.MarketShipment(
                        SubTransactionID=db_sub_transaction.SubTransactionID,
                        ProductTypeID=item.ProductTypeID,
                        ProductID=item.ProductID,
                        Price=item.Price,
                        InitialPrice=item.InitialPrice,
                        ShipmentStatus="awaiting"
                    )
                    db.add(db_market_shipment)
                    db.flush()

                    # Update product status to "Reserved"
                    locked_product.Status = "Reserved"
                    db.flush()
                    
                    successful_items.append(item)
                    
                except Exception as item_error:
                    failed_items.append({
                        "item": item.dict(),
                        "error": str(item_error)
                    })
                    continue
        
        # If no items were successful, rollback the entire transaction
        if not successful_items:
            db.rollback()
            raise HTTPException(
                status_code=400, 
                detail=f"No items could be processed successfully. Failed items: {len(failed_items)}"
            )
        
        # Commit the transaction
        db.commit()
        
        response = {
            "TransactionID": transaction_id,
            "message": f"Bulk transaction created successfully. {len(successful_items)} items processed, {len(failed_items)} failed.",
            "total_items": len(successful_items)
        }
        
        if failed_items:
            response["failed_items"] = failed_items
            
        return response

    except Exception as e:
        # Rollback on any error
        db.rollback()
        if "could not obtain lock" in str(e).lower():
            raise HTTPException(status_code=423, detail="Some products are currently being processed by another transaction. Please try again.")
        raise e


# Market Shipment CRUD functions
def get_market_shipments(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.MarketShipment).offset(skip).limit(limit).all()

def get_market_shipment_by_id(db: Session, market_shipment_id: int):
    return db.query(models.MarketShipment).filter(models.MarketShipment.MarketShipmentID == market_shipment_id).first()

def get_market_shipments_by_centra_id(db: Session, centra_id: str, skip: int = 0, limit: int = 10):
    return (
        db.query(models.MarketShipment)
        .join(models.SubTransaction, models.MarketShipment.SubTransactionID == models.SubTransaction.SubTransactionID)
        .filter(models.SubTransaction.CentraID == centra_id)
        .offset(skip)
        .limit(limit)
        .all()
    )

def update_market_shipment(db: Session, market_shipment_id: int, market_shipment_update: schemas.MarketShipmentUpdate):
    db_market_shipment = db.query(models.MarketShipment).filter(models.MarketShipment.MarketShipmentID == market_shipment_id).first()
    if not db_market_shipment:
        return None
    
    update_data = market_shipment_update.dict(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_market_shipment, field, value)
    
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

def update_market_shipment_status(db: Session, market_shipment_id: int, status: str):
    """Update the shipment status of a market shipment"""
    db_market_shipment = db.query(models.MarketShipment).filter(models.MarketShipment.MarketShipmentID == market_shipment_id).first()
    if not db_market_shipment:
        return None
    
    db_market_shipment.ShipmentStatus = status
    db.commit()
    db.refresh(db_market_shipment)
    return db_market_shipment

# --- Get All Transactions ---
def get_transactions(db: Session, skip: int = 0, limit: int = 10):
    return db.query(models.Transaction).offset(skip).limit(limit).all()

def get_transactions_by_customer(db: Session, skip: int = 0, limit: int = 10, session_data: schemas.SessionData = None):
    CustomerID = str(session_data.UserID)

    # First, get all transactions for this customer
    main_transactions = (
        db.query(models.Transaction)
        .filter(models.Transaction.CustomerID == CustomerID)
        .order_by(models.Transaction.CreatedAt.desc())
        .limit(limit)
        .offset(skip)
        .all()
    )
    
    if not main_transactions:
        return []

    result = []
    
    for main_transaction in main_transactions:
        # Get all sub-transactions and their related data for this transaction
        sub_transactions_data = (
            db.query(
                models.SubTransaction.SubTransactionID,
                models.SubTransaction.SubTransactionStatus,
                models.SubTransaction.CentraID,
                models.User.Username.label("CentraUsername"),
                models.MarketShipment.ProductID,
                models.MarketShipment.InitialPrice,
                models.MarketShipment.Price,
                models.MarketShipment.ShipmentStatus,
                models.Products.ProductName
            )
            .join(models.MarketShipment, models.SubTransaction.SubTransactionID == models.MarketShipment.SubTransactionID)
            .join(models.Products, models.MarketShipment.ProductTypeID == models.Products.ProductID)
            .join(models.User, models.SubTransaction.CentraID == models.User.UserID)
            .filter(models.SubTransaction.TransactionID == main_transaction.TransactionID)
            .all()
        )

        # Group the data by sub-transaction
        sub_transactions_dict = {}
        
        for row in sub_transactions_data:
            sub_tx_id = row.SubTransactionID
            
            # Get product weight based on product type
            product_weight = None
            if row.ProductName == "Wet Leaves":
                weight_result = db.query(models.WetLeaves.Weight).filter(models.WetLeaves.WetLeavesID == row.ProductID).first()
                product_weight = weight_result.Weight if weight_result else None
            elif row.ProductName == "Dry Leaves":
                weight_result = db.query(models.DryLeaves.Processed_Weight).filter(models.DryLeaves.DryLeavesID == row.ProductID).first()
                product_weight = weight_result.Processed_Weight if weight_result else None
            elif row.ProductName == "Powder":
                weight_result = db.query(models.Flour.Flour_Weight).filter(models.Flour.FlourID == row.ProductID).first()
                product_weight = weight_result.Flour_Weight if weight_result else None

            # Create market shipment data
            market_shipment = {
                "ProductID": row.ProductID,
                "InitialPrice": row.InitialPrice,
                "Price": row.Price,
                "Weight": product_weight,
                "ShipmentStatus": row.ShipmentStatus,
                "ProductName": row.ProductName
            }

            # If this sub-transaction doesn't exist in our dict, create it
            if sub_tx_id not in sub_transactions_dict:
                sub_transactions_dict[sub_tx_id] = {
                    "SubTransactionID": sub_tx_id,
                    "CentraUsername": row.CentraUsername,
                    "SubTransactionStatus": row.SubTransactionStatus,
                    "market_shipments": []
                }
            
            # Add the market shipment to this sub-transaction
            sub_transactions_dict[sub_tx_id]["market_shipments"].append(market_shipment)

        # Convert dictionary to list
        sub_transactions_list = list(sub_transactions_dict.values())

        transaction_data = {
            "TransactionID": main_transaction.TransactionID,
            "TransactionStatus": main_transaction.TransactionStatus,
            "CreatedAt": main_transaction.CreatedAt.isoformat(),
            "ExpirationAt": main_transaction.ExpirationAt.isoformat() if main_transaction.ExpirationAt else None,
            "sub_transactions": sub_transactions_list
        }
        
        result.append(transaction_data)

    return result

# --- Get Transaction by ID (basic) ---
def get_transaction_by_id(db: Session, transaction_id: UUID):
    return db.query(models.Transaction).filter(models.Transaction.TransactionID == str(transaction_id)).first()

def get_transaction_details_by_id(db: Session, transaction_id: UUID, session_data: schemas.SessionData = None, skip: int = 0, limit: int = 10):
    CustomerID = str(session_data.UserID)

    # First, get the main transaction details
    main_transaction = (
        db.query(models.Transaction)
        .filter(models.Transaction.CustomerID == CustomerID)
        .filter(models.Transaction.TransactionID == str(transaction_id))
        .first()
    )
    
    if main_transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    # Query to fetch all sub-transactions and their related data
    sub_transactions_data = (
        db.query(
            models.SubTransaction.SubTransactionID,
            models.SubTransaction.SubTransactionStatus,
            models.SubTransaction.CentraID,
            models.User.Username.label("CentraUsername"),
            models.MarketShipment.ProductID,
            models.MarketShipment.InitialPrice,
            models.MarketShipment.Price,
            models.MarketShipment.ShipmentStatus,
            models.Products.ProductName
        )
        .join(models.MarketShipment, models.SubTransaction.SubTransactionID == models.MarketShipment.SubTransactionID)
        .join(models.Products, models.MarketShipment.ProductTypeID == models.Products.ProductID)
        .join(models.User, models.SubTransaction.CentraID == models.User.UserID)
        .filter(models.SubTransaction.TransactionID == str(transaction_id))
        .all()
    )

    # Group the data by sub-transaction
    sub_transactions_dict = {}
    
    for row in sub_transactions_data:
        sub_tx_id = row.SubTransactionID
        
        # Get product weight based on product type
        product_weight = None
        if row.ProductName == "Wet Leaves":
            weight_result = db.query(models.WetLeaves.Weight).filter(models.WetLeaves.WetLeavesID == row.ProductID).first()
            product_weight = weight_result.Weight if weight_result else None
        elif row.ProductName == "Dry Leaves":
            weight_result = db.query(models.DryLeaves.Processed_Weight).filter(models.DryLeaves.DryLeavesID == row.ProductID).first()
            product_weight = weight_result.Processed_Weight if weight_result else None
        elif row.ProductName == "Powder":
            weight_result = db.query(models.Flour.Flour_Weight).filter(models.Flour.FlourID == row.ProductID).first()
            product_weight = weight_result.Flour_Weight if weight_result else None

        # Create market shipment data
        market_shipment = {
            "ProductID": row.ProductID,
            "InitialPrice": row.InitialPrice,
            "Price": row.Price,
            "Weight": product_weight,
            "ShipmentStatus": row.ShipmentStatus,
            "ProductName": row.ProductName
        }

        # If this sub-transaction doesn't exist in our dict, create it
        if sub_tx_id not in sub_transactions_dict:
            sub_transactions_dict[sub_tx_id] = {
                "SubTransactionID": sub_tx_id,
                "CentraUsername": row.CentraUsername,
                "SubTransactionStatus": row.SubTransactionStatus,
                "market_shipments": []
            }
        
        # Add the market shipment to this sub-transaction
        sub_transactions_dict[sub_tx_id]["market_shipments"].append(market_shipment)

    # Convert dictionary to list
    sub_transactions_list = list(sub_transactions_dict.values())

    transaction_data = {
        "TransactionID": main_transaction.TransactionID,
        "TransactionStatus": main_transaction.TransactionStatus,
        "CreatedAt": main_transaction.CreatedAt.isoformat(),
        "ExpirationAt": main_transaction.ExpirationAt.isoformat() if main_transaction.ExpirationAt else None,
        "sub_transactions": sub_transactions_list
    }

    return transaction_data

# --- Update Transaction ---
def update_transaction(db: Session, transaction_id: str, transaction_update: schemas.TransactionUpdate):
    db_transaction = db.query(models.Transaction).filter(models.Transaction.TransactionID == transaction_id).first()
    if not db_transaction:
        return None

    if transaction_update.status is not None:
        db_transaction.TransactionStatus = transaction_update.status

    db.commit()
    db.refresh(db_transaction)
    return db_transaction

def delete_transaction(db: Session, transaction_id: str):
    db_transaction = db.query(models.Transaction).options(
        selectinload(models.Transaction.sub_transactions)
        .selectinload(models.SubTransaction.market_shipments)
    ).filter(models.Transaction.TransactionID == transaction_id).first()

    if not db_transaction:
        return False

    for sub_transaction in db_transaction.sub_transactions:
        for market_shipment in sub_transaction.market_shipments:
            db.delete(market_shipment)
            print(f"Deleted MarketShipment ID: {market_shipment.MarketShipmentID}")

        db.delete(sub_transaction)
        print(f"Deleted SubTransaction ID: {sub_transaction.SubTransactionID}")

    db.delete(db_transaction)
    db.commit()
    print(f"Deleted Transaction ID: {db_transaction.TransactionID}")
    return True


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
    # Fetch data based on item type - only items with "Awaiting" status
    if item_type.lower() == 'flour':
        items = db.query(models.Flour).filter(models.Flour.Status == "Awaiting").order_by(func.random()).limit(limit).all()
        chosen_item = "Powder"
    elif item_type.lower() == 'dry_leaves':
        items = db.query(models.DryLeaves).filter(models.DryLeaves.Status == "Awaiting").order_by(func.random()).limit(limit).all()
        chosen_item = "Dry Leaves"
    else:
        raise ValueError("Invalid item type. Choose 'flour' or 'dry_leaves'.")

    # Initialize the dictionary to group items by user ID (centra ID)
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
       
        # Group by user_id (centra ID) instead of username
        if user_id not in grouped_data:
            grouped_data[user_id] = [item_data]
        else:
            grouped_data[user_id].append(item_data)

    return grouped_data

def get_items(db: Session, item_type: str, limit: int = 100):
    # Fetch data based on item type
    if item_type.lower() == 'flour':
        items = db.query(models.Flour).limit(limit).all()
    elif item_type.lower() == 'dry_leaves':
        items = db.query(models.DryLeaves).limit(limit).all()
    else:
        raise ValueError("Invalid item type. Choose 'flour' or 'dry_leaves'.")

    # Initialize the dictionary to group items by user ID (centra ID)
    grouped_data = {}

    # Iterate through each item to populate grouped_data
    for item in items:
        user_id = item.UserID  # Get the centra ID directly

        # Check item type to determine structure
        if item_type.lower() == 'dry_leaves':
            item_data = {"id": item.DryLeavesID, "weight": item.Processed_Weight}
        elif item_type.lower() == 'flour':
            item_data = {"id": item.FlourID, "weight": item.Flour_Weight}
       
        # Group by user_id (centra ID)
        if user_id not in grouped_data:
            grouped_data[user_id] = [item_data]
        else:
            grouped_data[user_id].append(item_data)

    return grouped_data

def get_items_by_selected_centra(db: Session, item_type: str, users: List[UUID]):
    # Convert UUIDs to strings to match the VARCHAR column type
    user_ids = [str(user_id) for user_id in users]
    if item_type.lower() == 'flour':
        items = db.query(models.Flour).filter(
            models.Flour.UserID.in_(user_ids),
            models.Flour.Status == "Awaiting"
        ).order_by(func.random()).all()
    elif item_type.lower() == 'dry_leaves':
        items = db.query(models.DryLeaves).filter(
            models.DryLeaves.UserID.in_(user_ids),
            models.DryLeaves.Status == "Awaiting"
        ).order_by(func.random()).all()
    else:
        raise ValueError("Invalid item type. Choose 'flour' or 'dry_leaves'.")

    grouped_data = {}

    for item in items:
        user_id = item.UserID
        
        item_data = {"id": item.DryLeavesID if item_type == 'dry_leaves' else item.FlourID,
                     "weight": item.Processed_Weight if item_type == 'dry_leaves' else item.Flour_Weight}
        
        if user_id not in grouped_data:
            grouped_data[user_id] = [item_data]
        else:
            grouped_data[user_id].append(item_data)

    return grouped_data

def get_random_centras(db: Session, numOfCentra: int):
    return db.query(models.User).filter(models.User.RoleID == 1).order_by(func.random()).limit(numOfCentra).all()

# Duplicate function removed - see implementation below

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

    # Initialize the dictionary to group items by user ID (centra ID)
    grouped_data = {}

    # Iterate through each item to populate grouped_data
    for item in items:
        user_id = item.UserID  # Get the centra ID directly

        # Check item type to determine structure
        if item_type.lower() == 'dry_leaves':
            item_data = {"id": item.DryLeavesID, "weight": item.Processed_Weight}
        elif item_type.lower() == 'flour':
            item_data = {"id": item.FlourID, "weight": item.Flour_Weight}
       
        # Group by user_id (centra ID)
        if user_id not in grouped_data:
            grouped_data[user_id] = [item_data]
        else:
            grouped_data[user_id].append(item_data)

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
        items: list[tuple[int, str, int, int, bool, int]] = []  # Keep str for centra_id (UUID string)
        memo.clear()
        next.clear()

        for centra_id, weights in item_weights.items():
            items += [
                (
                    item.get("weight", 0),
                    centra_id,
                    item.get("id", 0),
                    item.get("price", 0),
                    item.get("discounted", False),
                    item.get("initial_price", 0),  # Add `initial_price`
                )
                for item in weights
            ]

        max_value = dp(target_weight, 0, items)

        choices: dict[str, list[dict[str, int]]] = {}  # Keep str keys for UUID strings
        current = (target_weight, 0)

        while current in next:
            weight, centra_id, item_id, price, discounted, initial_price = items[current[1]]
            if next[current][2]:
                if centra_id not in choices:
                    choices[centra_id] = []
                choices[centra_id].append({
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
        
        for centra_id, weights in item_weights.items():
            items += [(item["weight"], centra_id, item["id"]) for item in weights]

        max_value = dp(target_weight, 0, items)
        
        choices: dict[str, list[dict[str, int]]] = {}
        current = (target_weight, 0)

        while next_choice.get(current):
            weight, centra_id, item_id = items[current[1]]
            if next_choice[current][2]:
                if centra_id not in choices:
                    choices[centra_id] = []
                choices[centra_id].append({"id": item_id, "weight": weight})
            current = next_choice[current][:2]
        
        return max_value, choices
    
    max_value, choices = knapsack(target_weight, all_data)
    
    return max_value, choices

def get_marketplace_items(db: Session, skip: int = 0, limit: int = 15):
    # Queries for individual products - only include available products
    wet = db.query(
        models.WetLeaves.WetLeavesID.label("id"),
        models.WetLeaves.UserID.label("user_id"),
        models.WetLeaves.Expiration.label("expiration"),
        models.WetLeaves.Weight.label("stock"),
        models.WetLeaves.Status.label("status"),
        literal_column("'Wet Leaves'").label("product_name")
    ).filter(models.WetLeaves.Status == "Awaiting")

    dry = db.query(
        models.DryLeaves.DryLeavesID.label("id"),
        models.DryLeaves.UserID.label("user_id"),
        models.DryLeaves.Expiration.label("expiration"),
        models.DryLeaves.Processed_Weight.label("stock"),
        models.DryLeaves.Status.label("status"),
        literal_column("'Dry Leaves'").label("product_name")
    ).filter(models.DryLeaves.Status == "Awaiting")

    flour = db.query(
        models.Flour.FlourID.label("id"),
        models.Flour.UserID.label("user_id"),
        models.Flour.Expiration.label("expiration"),
        models.Flour.Flour_Weight.label("stock"),
        models.Flour.Status.label("status"),
        literal_column("'Powder'").label("product_name")
    ).filter(models.Flour.Status == "Awaiting")

    # Combine queries with UNION ALL
    union_query = union_all(wet, dry, flour).alias("products")

    # Create an alias for the User table
    user_alias = aliased(models.User)

    # Create the full select statement with join to get username
    stmt = select(
        union_query.c.id,
        union_query.c.user_id,
        user_alias.Username.label("username"),
        union_query.c.expiration,
        union_query.c.product_name,
        union_query.c.stock,
        union_query.c.status
    ).join(user_alias, union_query.c.user_id == user_alias.UserID
    ).filter(
        union_query.c.expiration > func.now()  # Filter out expired products
    ).order_by(func.random()).offset(skip).limit(limit)

    # Execute the query
    rows = db.execute(stmt).fetchall()
    
    currentDate = datetime.now()
    results = []

    for row in rows:
        source = row.product_name
        centra_base_settings = get_centra_base_settings_by_user_id_and_items(db, row.user_id, source)
        discount_conditions = get_centra_setting_detail_by_user_id_and_item(db, row.user_id, source)

        price = centra_base_settings[0].InitialPrice if centra_base_settings else 0
        expdayleft = (row.expiration - currentDate).days

        def calculate_discounted_price(expiry_left, data, initial_price):
            applicable = [item for item in data if expiry_left <= item.ExpDayLeft]
            if not applicable:
                return initial_price
            best = min(applicable, key=lambda x: x.ExpDayLeft).DiscountRate
            return round(initial_price - (initial_price * best / 100))

        final_price = calculate_discounted_price(expdayleft, discount_conditions, price)

        results.append({
            "id": row.id,
            "product_name": row.product_name,
            "stock": row.stock,
            "centra_name": row.username,
            "initial_price": price,
            "price": final_price,
            "expiry_time": expdayleft,
            "status": row.status
        })

    return results

def get_product_details_by_product_id_and_product_name_and_username(db: Session, product_id: int, product_name: str, username: str):
    if product_name == 'Wet Leaves':
        product = (
            db.query(
                models.WetLeaves.WetLeavesID.label("id"),
                models.WetLeaves.UserID.label("user_id"),
                models.WetLeaves.Expiration.label("expiration"),
                models.WetLeaves.Weight.label("weight"),
                models.WetLeaves.Status.label("status"),
                literal_column("'Wet Leaves'").label("product_name"),
                models.User.Username.label("username"),
                models.User.UserID.label("centra_id"))
            .join(models.User, models.WetLeaves.UserID == models.User.UserID)
            .filter(
                models.WetLeaves.WetLeavesID == product_id,
                models.User.Username == username
            )
            .first()
        )

    elif product_name == 'Dry Leaves':
        product = (
            db.query( models.DryLeaves.DryLeavesID.label("id"),
                models.DryLeaves.UserID.label("user_id"),
                models.DryLeaves.Expiration.label("expiration"),
                models.DryLeaves.Processed_Weight.label("weight"),
                models.DryLeaves.Status.label("status"),
                literal_column("'Dry Leaves'").label("product_name"),
                models.User.Username.label("username"),
                models.User.UserID.label("centra_id"))
            .join(models.User, models.DryLeaves.UserID == models.User.UserID)
            .filter(
                models.DryLeaves.DryLeavesID == product_id,
                models.User.Username == username
            )
            .first()
        )

    elif product_name == 'Powder':
        product = (
            db.query(
                models.Flour.FlourID.label("id"),
                models.Flour.UserID.label("user_id"),
                models.Flour.Expiration.label("expiration"),
                models.Flour.Flour_Weight.label("weight"),
                models.Flour.Status.label("status"),
                literal_column("'Powder'").label("product_name"),
                models.User.Username.label("username"),
                models.User.UserID.label("centra_id"))
            .join(models.User, models.Flour.UserID == models.User.UserID)
            .filter(
                models.Flour.FlourID == product_id,
                models.User.Username == username
            )
            .first()
        )
    else:
        raise HTTPException(status_code=400, detail="Invalid product type")

    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    
    currentDate = datetime.now()

    source = product.product_name
    centra_base_settings = get_centra_base_settings_by_user_id_and_items(db, product.user_id, source)
    discount_conditions = get_centra_setting_detail_by_user_id_and_item(db, product.user_id, source)

    price = centra_base_settings[0].InitialPrice if centra_base_settings else 0
    expdayleft = (product.expiration - currentDate).days

    def calculate_discounted_price(expiry_left, data, initial_price):
        applicable = [item for item in data if expiry_left <= item.ExpDayLeft]
        if not applicable:
            return initial_price
        best = min(applicable, key=lambda x: x.ExpDayLeft).DiscountRate
        return round(initial_price - (initial_price * best / 100))

    final_price = calculate_discounted_price(expdayleft, discount_conditions, price)

    return {
        "id": product.id,
        "product_name": product.product_name,
        "weight": product.weight,
        "centra_name": product.username,
        "initial_price": price,
        "price": final_price,
        "expiry_time": expdayleft,
        "centra_id": product.centra_id,
        "status": product.status
    }
    
def create_new_transaction(db: Session, market_shipment: schemas.MarketShipmentCreate):
    centra_id_str = str(market_shipment.CentraID)
    customer_id_str = str(market_shipment.CustomerID)

    # Validate Centra user
    centra_user = db.query(models.User).filter(models.User.UserID == centra_id_str).first()
    if not centra_user or centra_user.RoleID != 1:
        raise HTTPException(status_code=400, detail="CentraID must reference a user with the 'Centra' role.")

    # Validate Customer user
    customer_user = db.query(models.User).filter(models.User.UserID == customer_id_str).first()
    if not customer_user or customer_user.RoleID != 5:
        raise HTTPException(status_code=400, detail="CustomerID must reference a user with the 'Customer' role.")

    # Database transaction with row-level locking
    try:
        # Lock the specific product row to prevent concurrent modifications
        product_table = None
        product_query = None
        
        if market_shipment.ProductTypeID == 1:  # Wet Leaves
            product_table = models.WetLeaves
            product_query = db.query(models.WetLeaves).filter(
                models.WetLeaves.WetLeavesID == market_shipment.ProductID
            ).with_for_update(nowait=False)
        elif market_shipment.ProductTypeID == 2:  # Dry Leaves
            product_table = models.DryLeaves
            product_query = db.query(models.DryLeaves).filter(
                models.DryLeaves.DryLeavesID == market_shipment.ProductID
            ).with_for_update(nowait=False)
        elif market_shipment.ProductTypeID == 3:  # Flour
            product_table = models.Flour
            product_query = db.query(models.Flour).filter(
                models.Flour.FlourID == market_shipment.ProductID
            ).with_for_update(nowait=False)
        else:
            raise HTTPException(status_code=400, detail="Invalid ProductTypeID")

        # Lock and validate the product exists and is available
        locked_product = product_query.first()
        if not locked_product:
            raise HTTPException(status_code=404, detail="Product not found")
        
        # Check if product is available (not already processed or sold)
        if hasattr(locked_product, 'Status') and locked_product.Status in ['Processed', 'Sold', 'Expired', 'Reserved']:
            raise HTTPException(status_code=400, detail=f"Product is not available. Current status: {locked_product.Status}")

        # Check product ownership belongs to the centra
        if locked_product.UserID != centra_id_str:
            raise HTTPException(status_code=403, detail="Product does not belong to the specified centra")

        # Step 1: Create Transaction (✅ now includes CustomerID)
        transaction_id = str(uuid.uuid4())
        db_transaction = models.Transaction(
            TransactionID=transaction_id,
            CustomerID=customer_id_str  # ✅ moved here
        )
        db.add(db_transaction)
        db.flush()  # Use flush instead of commit to keep transaction open

        # Step 2: Create SubTransaction linked to the Transaction
        db_sub_transaction = models.SubTransaction(
            TransactionID=transaction_id,
            CentraID=market_shipment.CentraID
        )
        db.add(db_sub_transaction)
        db.flush()

        # Step 3: Create MarketShipment linked to the SubTransaction (✅ no more CustomerID here)
        db_market_shipment = models.MarketShipment(
            SubTransactionID=db_sub_transaction.SubTransactionID,
            ProductTypeID=market_shipment.ProductTypeID,
            ProductID=market_shipment.ProductID,
            Price=market_shipment.Price,
            InitialPrice=market_shipment.InitialPrice,
        )
        db.add(db_market_shipment)
        db.flush()

        # Update product status to "Reserved" to indicate it's part of a transaction
        locked_product.Status = "Reserved"
        db.flush()

        # Commit the entire transaction
        db.commit()

        return {
            "transaction": db_transaction,
            "sub_transaction": db_sub_transaction,
            "market_shipment": db_market_shipment,
            "message": "Transaction created successfully with product locked"
        }

    except Exception as e:
        # Rollback on any error
        db.rollback()
        if "could not obtain lock" in str(e).lower():
            raise HTTPException(status_code=423, detail="Product is currently being processed by another transaction. Please try again.")
        raise e

def get_trx_id(db: Session, trx: schemas.blockchain_schemas):
    # Save the mapping between user_id and blockchain trx id
    db_trx = models.BlockchainTrx(
        UserID=trx.userId,
        TrxId=trx.trx_id
    )
    db.add(db_trx)
    db.commit()
    db.refresh(db_trx)
    return db_trx

# blockchain transactions
def create_blockchain_trx(db: Session, user_id: str, trx_id: str):
    db_trx = models.BlockchainTrx(
        UserID=user_id,
        TrxId=trx_id
    )
    db.add(db_trx)
    db.commit()
    db.refresh(db_trx)
    return db_trx

def get_blockchain_trx_by_user_id(db: Session, user_id: str):
    return db.query(models.BlockchainTrx).filter(models.BlockchainTrx.UserID == user_id).all()

def get_blockchain_trx_by_trx_id(db: Session, trx_id: str):
    return db.query(models.BlockchainTrx).filter(models.BlockchainTrx.TrxId == trx_id).first()

def get_all_blockchain_trx(db: Session):
    return db.query(models.BlockchainTrx).all()

# Product status management with row-level locking
def update_product_status_with_lock(db: Session, product_type_id: int, product_id: int, new_status: str):
    """Update product status with row-level locking to prevent concurrent modifications"""
    try:
        # Lock the specific product row
        if product_type_id == 1:  # Wet Leaves
            product = db.query(models.WetLeaves).filter(
                models.WetLeaves.WetLeavesID == product_id
            ).with_for_update(nowait=False).first()
        elif product_type_id == 2:  # Dry Leaves
            product = db.query(models.DryLeaves).filter(
                models.DryLeaves.DryLeavesID == product_id
            ).with_for_update(nowait=False).first()
        elif product_type_id == 3:  # Flour
            product = db.query(models.Flour).filter(
                models.Flour.FlourID == product_id
            ).with_for_update(nowait=False).first()
        else:
            raise HTTPException(status_code=400, detail="Invalid ProductTypeID")

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Update the status
        product.Status = new_status
        db.flush()
        db.commit()
        
        return product

    except Exception as e:
        db.rollback()
        if "could not obtain lock" in str(e).lower():
            raise HTTPException(status_code=423, detail="Product is currently being processed. Please try again.")
        raise e

def complete_transaction_and_process_product(db: Session, transaction_id: str, user_id: str):
    """Complete a transaction and update product status to 'Processed' with proper locking"""
    try:
        # Lock and get the transaction
        transaction = db.query(models.Transaction).filter(
            models.Transaction.TransactionID == transaction_id
        ).with_for_update(nowait=False).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Get all market shipments for this transaction
        market_shipments = (
            db.query(models.MarketShipment)
            .join(models.SubTransaction)
            .filter(models.SubTransaction.TransactionID == transaction_id)
            .with_for_update(nowait=False)
            .all()
        )
        
        # Update each product in the transaction to "Processed"
        for shipment in market_shipments:
            # Lock the specific product
            if shipment.ProductTypeID == 1:  # Wet Leaves
                product = db.query(models.WetLeaves).filter(
                    models.WetLeaves.WetLeavesID == shipment.ProductID
                ).with_for_update(nowait=False).first()
            elif shipment.ProductTypeID == 2:  # Dry Leaves
                product = db.query(models.DryLeaves).filter(
                    models.DryLeaves.DryLeavesID == shipment.ProductID
                ).with_for_update(nowait=False).first()
            elif shipment.ProductTypeID == 3:  # Flour
                product = db.query(models.Flour).filter(
                    models.Flour.FlourID == shipment.ProductID
                ).with_for_update(nowait=False).first()
            
            if product:
                product.Status = "Processed"
                shipment.ShipmentStatus = "processed"
        
        # Update transaction status
        transaction.TransactionStatus = "Completed"
        
        db.flush()
        db.commit()
        
        return {
            "message": "Transaction completed and products processed successfully",
            "transaction_id": transaction_id,
            "processed_products": len(market_shipments)
        }

    except Exception as e:
        db.rollback()
        if "could not obtain lock" in str(e).lower():
            raise HTTPException(status_code=423, detail="Transaction or products are currently being processed. Please try again.")
        raise e

def cancel_transaction_and_release_products(db: Session, transaction_id: str, user_id: str):
    """Cancel a transaction and release locked products back to available status"""
    try:
        # Lock and get the transaction
        transaction = db.query(models.Transaction).filter(
            models.Transaction.TransactionID == transaction_id
        ).with_for_update(nowait=False).first()
        
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Verify user has permission to cancel (either customer or centra)
        sub_transactions = db.query(models.SubTransaction).filter(
            models.SubTransaction.TransactionID == transaction_id
        ).all()
        
        has_permission = False
        if transaction.CustomerID == user_id:
            has_permission = True
        
        for sub_trans in sub_transactions:
            if sub_trans.CentraID == user_id:
                has_permission = True
                break
        
        if not has_permission:
            raise HTTPException(status_code=403, detail="You don't have permission to cancel this transaction")
        
        # Get all market shipments for this transaction
        market_shipments = (
            db.query(models.MarketShipment)
            .join(models.SubTransaction)
            .filter(models.SubTransaction.TransactionID == transaction_id)
            .with_for_update(nowait=False)
            .all()
        )
        
        # Release each product back to available status
        for shipment in market_shipments:
            # Lock the specific product
            if shipment.ProductTypeID == 1:  # Wet Leaves
                product = db.query(models.WetLeaves).filter(
                    models.WetLeaves.WetLeavesID == shipment.ProductID
                ).with_for_update(nowait=False).first()
            elif shipment.ProductTypeID == 2:  # Dry Leaves
                product = db.query(models.DryLeaves).filter(
                    models.DryLeaves.DryLeavesID == shipment.ProductID
                ).with_for_update(nowait=False).first()
            elif shipment.ProductTypeID == 3:  # Flour
                product = db.query(models.Flour).filter(
                    models.Flour.FlourID == shipment.ProductID
                ).with_for_update(nowait=False).first()
            
            if product and product.Status == "Reserved":
                product.Status = "Awaiting"  # Release back to available
                shipment.ShipmentStatus = "cancelled"
        
        # Update transaction status
        transaction.TransactionStatus = "Cancelled"
        
        db.flush()
        db.commit()
        
        return {
            "message": "Transaction cancelled and products released successfully",
            "transaction_id": transaction_id,
            "released_products": len(market_shipments)
        }

    except Exception as e:
        db.rollback()
        if "could not obtain lock" in str(e).lower():
            raise HTTPException(status_code=423, detail="Transaction or products are currently being processed. Please try again.")
        raise e

def get_product_lock_status(db: Session, product_type_id: int, product_id: int):
    """Check if a product is currently locked (reserved) in any active transaction"""
    try:
        # Check if product exists and get its current status
        if product_type_id == 1:  # Wet Leaves
            product = db.query(models.WetLeaves).filter(
                models.WetLeaves.WetLeavesID == product_id
            ).first()
        elif product_type_id == 2:  # Dry Leaves
            product = db.query(models.DryLeaves).filter(
                models.DryLeaves.DryLeavesID == product_id
            ).first()
        elif product_type_id == 3:  # Flour
            product = db.query(models.Flour).filter(
                models.Flour.FlourID == product_id
            ).first()
        else:
            raise HTTPException(status_code=400, detail="Invalid ProductTypeID")

        if not product:
            raise HTTPException(status_code=404, detail="Product not found")

        # Check if product is in any active transactions
        active_shipments = (
            db.query(models.MarketShipment)
            .join(models.SubTransaction)
            .join(models.Transaction)
            .filter(
                models.MarketShipment.ProductTypeID == product_type_id,
                models.MarketShipment.ProductID == product_id,
                models.Transaction.TransactionStatus.in_(["Transaction Pending", "Processing"])
            )
            .first()
        )

        return {
            "product_id": product_id,
            "product_type_id": product_type_id,
            "current_status": product.Status,
            "is_locked": product.Status == "Reserved" or active_shipments is not None,
            "active_transaction": active_shipments.sub_transaction.TransactionID if active_shipments else None
        }

    except Exception as e:
        raise e