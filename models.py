from sqlalchemy import CheckConstraint, Column, Integer, String, Text, ForeignKey, Float, DateTime, Enum, BigInteger, Table, func
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy import Column, Integer, String, ForeignKey, UUID, Boolean

Base = declarative_base()

# Association table for many-to-many relationship between Shipments and Flour
shipment_flour_association = Table(
    'shipment_flour_association', Base.metadata,
    Column('shipment_id', Integer, ForeignKey('shipments.ShipmentID')),
    Column('flour_id', Integer, ForeignKey('flour.FlourID'))
)

class SessionData(Base):
    __tablename__ = "sessions"

    session_id = Column(String(36), unique=True, primary_key=True)
    user_id = Column(String(36), ForeignKey('users.UserID'))
    user_role = Column(Integer, ForeignKey('roles.RoleID'))
    user_email = Column(String(36))

class OTP(Base):
    __tablename__ = "otp"

    email = Column(String, primary_key=True, index=True)
    otp_code = Column(String, nullable=False)
    expires_at = Column(DateTime, nullable=False, default=func.now())

class RoleModel(Base):
    __tablename__ = "roles"
    
    RoleID = Column(Integer, primary_key=True)
    RoleName = Column(String(50))

class User(Base):
    __tablename__ = "users"

    UserID = Column(String(36), primary_key=True) 
    Username = Column(String(50))
    Email = Column(String(100), unique=True)
    PhoneNumber = Column(BigInteger)
    Password = Column(String(100))
    RoleID = Column(Integer, ForeignKey('roles.RoleID'))
    role = relationship("RoleModel")
    finances = relationship("CentraFinance", back_populates="user")  # Add this line
    
    
class Location(Base):
    __tablename__ = "locations"

    user_id = Column(String(36), ForeignKey("users.UserID"), primary_key=True)
    location_address = Column(String(100))
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)

class Courier(Base):
    __tablename__ = "couriers"
    
    CourierID = Column(Integer, primary_key=True, autoincrement=True) 
    CourierName = Column(String(50), nullable=False)

class WetLeaves(Base):
    __tablename__ = "wet_leaves"

    WetLeavesID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(String(36), ForeignKey("users.UserID"))
    Weight = Column(Float)
    ReceivedTime = Column(DateTime)
    Expiration = Column(DateTime)
    Status = Column(String(50), default="Awaiting")

class DryLeaves(Base):
    __tablename__ = "dry_leaves"

    DryLeavesID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(String(36), ForeignKey("users.UserID"))
    WetLeavesID = Column(Integer, ForeignKey("wet_leaves.WetLeavesID"))
    Processed_Weight = Column(Float)
    Expiration = Column(DateTime, nullable=True)
    Status = Column(String(50), default="Awaiting")

class Flour(Base):
    __tablename__ = "flour"

    FlourID = Column(Integer, primary_key=True, autoincrement=True)
    DryLeavesID = Column(Integer, ForeignKey("dry_leaves.DryLeavesID"))
    UserID = Column(String(36), ForeignKey("users.UserID"))
    Flour_Weight = Column(Float)
    Expiration = Column(DateTime, nullable=True)
    Status = Column(String(50), default="Awaiting")

class Shipment(Base):
    __tablename__ = "shipments"

    ShipmentID = Column(Integer, primary_key=True, autoincrement=True)
    CourierID = Column(Integer, ForeignKey("couriers.CourierID"))
    UserID = Column(String(36), ForeignKey("users.UserID"))
    ShipmentQuantity = Column(Integer)
    ShipmentDate = Column(DateTime, nullable=True)
    Check_in_Date = Column(DateTime, nullable=True)
    Check_in_Quantity = Column(Integer, nullable=True)
    Harbor_Reception_File = Column(Boolean,nullable=True)
    Rescalled_Weight = Column(Float, nullable=True)
    Rescalled_Date = Column(DateTime, nullable=True)
    Centra_Reception_File = Column(Boolean,nullable=True)
    
    flours = relationship("Flour", secondary=shipment_flour_association, backref="shipments")
   
   
#marketplace 

class AdminSettings(Base):
    __tablename__ = "admin_settings"

    AdminSettingsID = Column(Integer, primary_key=True, autoincrement=True)
    AdminFeeValue = Column(Float, nullable=False)


class Products(Base):
    __tablename__ = "products_templates"

    ProductID = Column(Integer, primary_key=True, autoincrement=True)
    ProductName = Column(String(100), nullable=False)

class CentraBaseSettings(Base):
    __tablename__ = "centra_base_settings"

    SettingsID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(String(36), ForeignKey("users.UserID"))
    ProductID = Column(Integer, ForeignKey("products_templates.ProductID"))
    InitialPrice = Column(Float, nullable=False)
    Sellable = Column(Boolean, nullable=False, default=True)  

    products_templates = relationship("Products", backref="base_settings")


class CentraSettingDetail(Base):
    __tablename__ = "centra_setting_details"

    SettingDetailID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(String(36), ForeignKey("users.UserID"))
    ProductID = Column(Integer, ForeignKey("products_templates.ProductID"))
    DiscountRate = Column(Integer)
    ExpDayLeft = Column(Integer)

    products_templates = relationship("Products", backref="setting_details")
    
class MarketShipment(Base):
    __tablename__ = "market_shipment"

    MarketShipmentID = Column(Integer, primary_key=True, autoincrement=True)
    CentraID = Column(String(36), ForeignKey('users.UserID'))
    CustomerID = Column(String(36), ForeignKey('users.UserID'))
    DryLeavesID = Column(Integer, ForeignKey('dry_leaves.DryLeavesID'), nullable=True)
    PowderID = Column(Integer, ForeignKey('flour.FlourID'), nullable=True)
    status = Column(String)

    __table_args__ = (
        CheckConstraint(
            '(DryLeavesID IS NULL AND PowderID IS NOT NULL) OR (DryLeavesID IS NOT NULL AND PowderID IS NULL)',
            name='only_one_product_constraint'
        ),
    )
    
class SubTransaction(Base):
    __tablename__ = "sub_transaction"
    
    SubTransactionID = Column(Integer, primary_key=True, autoincrement=True)
    MarketShipmentID = Column(Integer, ForeignKey("market_shipment.MarketShipmentID"))
    status = Column(String)

    # Relationship to Transaction model
    transactions = relationship("Transaction", back_populates="sub_transaction")

class Transaction(Base):
    __tablename__ = "transaction"
    
    TransactionID = Column(Integer, primary_key=True, autoincrement=True)
    SubTransactionID = Column(Integer, ForeignKey("sub_transaction.SubTransactionID"))
    status = Column(String)
    
    # Relationship to SubTransaction model
    sub_transaction = relationship("SubTransaction", back_populates="transactions")

class CentraFinance(Base):
    __tablename__ = "centra_finance"

    FinanceID = Column(Integer, primary_key=True, autoincrement=True)
    UserID = Column(String(36), ForeignKey("users.UserID"), nullable=False)  
    AccountHolderName = Column(String(100), nullable=False)
    BankCode = Column(String(20), nullable=False)
    BankAccountNumber = Column(String(16), nullable=False)

    user = relationship("User", back_populates="finances")


# Transaction Table: TransactionID, SubTransactionID, s


# class IndonesianCity(Base):
#     __tablename__ = "indonesian_cities"
#     user_id = Column(String, ForeignKey("users.UserID"), primary_key=True)
#     name = Column(String, nullable=True)
#     lat = Column(Float, nullable=True)
#     lng = Column(Float, nullable=True)

#     user = relationship("User", back_populates="cities")
