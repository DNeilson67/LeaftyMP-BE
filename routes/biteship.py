from fastapi import APIRouter, HTTPException
import httpx
from schemas import ShipmentData  
from dotenv import load_dotenv
import os

router = APIRouter()

load_dotenv()

BITESHIP_API_KEY = os.getenv("BITESHIP_API_KEY")
HEADERS = {
    "Authorization": BITESHIP_API_KEY,
    "Content-Type": "application/json"
}

@router.post("/create-shipment")
async def create_shipment(shipment: ShipmentData):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                "https://api.biteship.com/v1/orders",
                headers=HEADERS,
                json=shipment.dict()
            )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/get-shipment/{tracking_id}")
async def get_shipment(tracking_id: str):
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.biteship.com/v1/orders/{tracking_id}",
                headers=HEADERS
            )
        if response.status_code != 200:
            raise HTTPException(status_code=response.status_code, detail=response.text)
        return response.json()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
