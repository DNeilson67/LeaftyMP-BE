import base64
from typing import Dict, List, Optional
from fastapi import APIRouter, Depends, Form, HTTPException, Request, Response, Body
import requests
import httpx
import pandas as pd
from sqlalchemy.orm import Session
from datetime import datetime
import crud
from database import get_db
from schemas.xendit_schemas import InvoiceRequest, XenditInvoiceRequestBody, InvoicePaidWebhook
import models 
from models import Flour,WetLeaves,DryLeaves
from dotenv import load_dotenv
import os

router = APIRouter()

load_dotenv()

# Load and encode logo
with open("./LeaftyLogo.svg", "rb") as logo_file:
    encoded_logo = base64.b64encode(logo_file.read()).decode('utf-8')

# Xendit credentials
XENDIT_API_KEY = os.getenv("XENDIT_API_KEY")
INVOICE_API_KEY = os.getenv("INVOICE_API_KEY")
INVOICE_API_URL = "https://invoice-generator.com"
encoded_api_key = base64.b64encode(f"{XENDIT_API_KEY}:".encode()).decode()
xendit_invoice_url = "https://api.xendit.co/v2/invoices"


@router.post("/create_invoice", tags=["Xendit"])
async def create_invoice(invoice_request: InvoiceRequest):
    headers = {
        "Authorization": f"Basic {encoded_api_key}"
    }
    data = invoice_request.dict()

    try:
        response = requests.post(xendit_invoice_url, json=data, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail="Error creating invoice with Xendit")


@router.get('/invoices/get')
async def get_invoices(limit: Optional[int] = None):
    try:
        headers = {
            "Authorization": f"Basic {encoded_api_key}",
            'Content-Type': 'application/json',
        }
        params = {}
        if limit:
            params['limit'] = limit

        async with httpx.AsyncClient() as client:
            response = await client.get(xendit_invoice_url, headers=headers, params=params)
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(status_code=e.response.status_code, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invoice/generate")
async def generate_invoice(
    from_info: str = Form(...),
    to_info: str = Form(...),
    date: str = Form(...),
    due_date: Optional[str] = Form(None),
    number: Optional[str] = Form(None),
    currency: Optional[str] = Form("USD"),
    logo: Optional[str] = Form(None),
    notes: Optional[str] = Form(None),
    terms: Optional[str] = Form(None),
    payment_terms: Optional[str] = Form(None),
    tax: Optional[float] = Form(0),
    discounts: Optional[float] = Form(0),
    shipping: Optional[float] = Form(0),
    amount_paid: Optional[float] = Form(0),
    item_names: List[str] = Form(...),
    item_quantities: List[int] = Form(...),
    item_unit_costs: List[float] = Form(...)
):
    # Validate items
    if not (len(item_names) == len(item_quantities) == len(item_unit_costs)):
        raise HTTPException(status_code=400, detail="Item fields must have the same length.")

    # Build line items
    items = [
        {"name": item_names[i], "quantity": item_quantities[i], "unit_cost": item_unit_costs[i]}
        for i in range(len(item_names))
    ]

    # Prepare payload
    payload = {
        "logo": logo,
        "from": from_info,
        "to": to_info,
        "number": number,
        "currency": currency,
        "date": date,
        "due_date": due_date,
        "payment_terms": payment_terms,
        "items": items,
        "tax": tax,
        "discounts": discounts,
        "shipping": shipping,
        "amount_paid": amount_paid,
        "notes": notes,
        "terms": terms
    }

    # Remove keys with None values
    payload = {k: v for k, v in payload.items() if v is not None}
    headers = {
        "Authorization": f"Bearer {INVOICE_API_KEY}"
    }

    try:
        # Send POST request to Invoice Generator API
        async with httpx.AsyncClient() as client:
            response = await client.post(INVOICE_API_URL, json=payload, headers=headers)

            if response.status_code == 200:
                return Response(
                    content=response.content,
                    media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename=invoice_{number or 'generated'}.pdf"}
                )
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to create invoice.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/invoice/from_webhook")
async def generate_invoice_from_webhook(payload: XenditInvoiceRequestBody):
    try:
        from_info = payload.merchant_name or "Merchant"
        to_info = payload.payer_email or "Customer"
        date = payload.created.isoformat() if payload.created else ""
        due_date = payload.paid_at.isoformat() if payload.paid_at else ""
        number = payload.external_id or ""
        currency = payload.currency or "USD"
        amount_paid = payload.paid_amount or 0
        description = payload.description or "No description"
        tax = 0
        discounts = 0
        shipping = 0

        # Prepare item list from description (for simplicity)
        item_names = [description]
        item_quantities = [1]
        item_unit_costs = [payload.amount or 0]

        invoice_payload = {
            "logo": encoded_logo,
            "from": from_info,
            "to": to_info,
            "number": number,
            "currency": currency,
            "date": pd.to_datetime(date).strftime('%d/%m/%Y - %H:%M:%S') if date else "",
            "due_date": pd.to_datetime(due_date).strftime('%d/%m/%Y - %H:%M:%S') if due_date else "",
            "items": [{"name": item_names[0], "quantity": item_quantities[0], "unit_cost": item_unit_costs[0]}],
            "tax": 0,
            "discounts": 0,
            "shipping": 0,
            "amount_paid": amount_paid,
            "notes": f"Payment via {payload.payment_method}",
            "terms": "Thank you for your business!"
        }

        invoice_payload = {k: v for k, v in invoice_payload.items() if v is not None}
        headers = {
            "Authorization": f"Bearer {INVOICE_API_KEY}"
        }

        # Send POST request to Invoice Generator API
        async with httpx.AsyncClient() as client:
            response = await client.post(INVOICE_API_URL, json=invoice_payload, headers=headers)

            if response.status_code == 200:
                return Response(
                    content=response.content,
                    media_type="application/pdf",
                    headers={"Content-Disposition": f"attachment; filename=invoice_{number or 'generated'}.pdf"}
                )
            else:
                raise HTTPException(status_code=response.status_code, detail="Failed to create invoice.")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/payout_channels/get")
async def get_payout_channels():
    headers = {
        "Authorization": f"Basic {encoded_api_key}",
        'Content-Type': 'application/json',
    }

    params = {"currency": "IDR", "channel_category": "BANK"}
    response = requests.get("https://api.xendit.co/payouts_channels", headers=headers, params=params)

    if response.status_code == 200:
        return response.json()
    else:
        raise HTTPException(status_code=response.status_code, detail="Failed to get payout channels")


@router.get("/invoices/test")
def test():
    return {"message": "Triggered"}


#WEBHOOK: Change status to "On Delivery" if paid
@router.post("/webhook/invoice-paid", tags=["Xendit Webhooks"])
async def invoice_paid_webhook(payload: InvoicePaidWebhook, db: Session = Depends(get_db)):
    try:
        if payload.status != "PAID":
            return {"message": f"Ignored. Status is {payload.status}"}
        
        transaction_id = payload.external_id.split('_')[-1]

        transaction = db.query(models.Transaction).filter_by(TransactionID=transaction_id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        transaction.TransactionStatus = "On Delivery"

        for sub_tx in transaction.sub_transactions:
            sub_tx.SubTransactionStatus = "On Delivery"  
            for shipment in sub_tx.market_shipments:
                shipment.ShipmentStatus = "On Delivery"

                if shipment.ProductTypeID == 1:
                    wetleaf = db.query(WetLeaves).filter_by(WetLeavesID=shipment.ProductID).first()
                    if wetleaf:
                        wetleaf.Status = "On Delivery"

                elif shipment.ProductTypeID == 2:
                    dryleaf = db.query(DryLeaves).filter_by(DryLeavesID=shipment.ProductID).first()
                    if dryleaf:
                        dryleaf.Status = "On Delivery"

                elif shipment.ProductTypeID == 3:
                    flour = db.query(Flour).filter_by(FlourID=shipment.ProductID).first()
                    if flour:
                        flour.Status = "On Delivery"

        db.commit()
        return {"message": f"Transaction {transaction_id} and related products updated to 'On Delivery'"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")

