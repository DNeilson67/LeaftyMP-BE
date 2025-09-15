# Biteship schemas
from pydantic import BaseModel
from typing import List, Dict, Optional

class Coordinates(BaseModel):
    latitude: float
    longitude: float

class Item(BaseModel):
    name: str
    description: str
    category: str
    value: int
    quantity: int
    height: int
    length: int
    weight: int
    width: int

class ShipmentData(BaseModel):
    shipper_contact_name: str
    shipper_contact_phone: str
    shipper_contact_email: str
    shipper_organization: str
    origin_contact_name: str
    origin_contact_phone: str
    origin_address: str
    origin_note: str
    origin_coordinate: Coordinates
    destination_contact_name: str
    destination_contact_phone: str
    destination_contact_email: str
    destination_address: str
    destination_note: str
    destination_coordinate: Coordinates
    courier_company: str
    courier_type: str
    courier_insurance: int
    delivery_type: str
    order_note: str
    metadata: Dict = {}
    items: List[Item]
