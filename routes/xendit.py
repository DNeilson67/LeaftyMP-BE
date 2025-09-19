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
import logging
from email_service import EmailService, create_receipt_email_body

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


@router.post("/test-receipt/{transaction_id}", tags=["Testing"])
async def test_receipt_email(transaction_id: str, db: Session = Depends(get_db)):
    """Test endpoint to manually send receipt for a transaction"""
    try:
        # Get transaction
        transaction = db.query(models.Transaction).filter_by(TransactionID=transaction_id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Get customer
        customer = db.query(models.User).filter_by(UserID=transaction.CustomerID).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get transaction details
        transaction_details = crud.get_transaction_details_by_id(
            db=db, 
            transaction_id=transaction_id, 
            session_data=type('obj', (object,), {'UserID': transaction.CustomerID})()
        )
        
        # Create mock payment payload for testing
        mock_payload = type('obj', (object,), {
            'paid_at': datetime.now(),
            'payment_method': 'Test Payment'
        })()
        
        # Generate PDF receipt
        receipt_pdf = await generate_receipt_pdf(transaction_details, customer, mock_payload)
        
        # Send email
        email_service = EmailService()
        email_subject = f"🧾 Test Receipt for Order #{transaction_id[:8]} - Leafty"
        email_body = create_receipt_email_body(transaction_details, customer.Username)
        
        email_sent = email_service.send_email_with_attachment(
            to_email=customer.Email,
            subject=email_subject,
            body=email_body,
            attachment_content=receipt_pdf,
            attachment_filename=f"test_receipt_{transaction_id}.pdf"
        )
        
        print(email_sent)
        
        if email_sent:
            return {"message": f"Test receipt sent successfully to {customer.Email}"}
        else:
            raise HTTPException(status_code=500, detail="Failed to send test receipt")
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Test receipt failed: {str(e)}")


@router.get("/receipt/{transaction_id}", tags=["Receipts"])
async def download_receipt(transaction_id: str, db: Session = Depends(get_db)):
    """Download receipt PDF for a transaction"""
    try:
        # Get transaction
        transaction = db.query(models.Transaction).filter_by(TransactionID=transaction_id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Get customer
        customer = db.query(models.User).filter_by(UserID=transaction.CustomerID).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")
        
        # Get transaction details
        transaction_details = crud.get_transaction_details_by_id(
            db=db, 
            transaction_id=transaction_id, 
            session_data=type('obj', (object,), {'UserID': transaction.CustomerID})()
        )
        
        # Create mock payment payload
        mock_payload = type('obj', (object,), {
            'paid_at': datetime.now(),
            'payment_method': 'Xendit Payment'
        })()
        
        # Generate PDF receipt
        receipt_pdf = await generate_receipt_pdf(transaction_details, customer, mock_payload)
        
        return Response(
            content=receipt_pdf,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename=receipt_{transaction_id}.pdf"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Receipt generation failed: {str(e)}")


#WEBHOOK: Change status to "On Delivery" if paid and send receipt
@router.post("/webhook/invoice-paid", tags=["Xendit Webhooks"])
async def invoice_paid_webhook(payload: InvoicePaidWebhook, db: Session = Depends(get_db)):
    try:
        if payload.status != "PAID":
            return {"message": f"Ignored. Status is {payload.status}"}
        
        transaction_id = payload.external_id.split('_')[-1]

        # Get transaction with full details
        transaction = db.query(models.Transaction).filter_by(TransactionID=transaction_id).first()
        if not transaction:
            raise HTTPException(status_code=404, detail="Transaction not found")
        
        # Get customer details
        customer = db.query(models.User).filter_by(UserID=transaction.CustomerID).first()
        if not customer:
            raise HTTPException(status_code=404, detail="Customer not found")

        # Update transaction status
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

        # Generate and send receipt
        try:
            # Get full transaction details for receipt
            transaction_details = crud.get_transaction_details_by_id(
                db=db, 
                transaction_id=transaction_id, 
                session_data=type('obj', (object,), {'UserID': transaction.CustomerID})()
            )
            
            # Generate PDF receipt
            receipt_pdf = await generate_receipt_pdf(transaction_details, customer, payload)
            
            # Send email with receipt
            email_service = EmailService()
            email_subject = f"🧾 Receipt for Order #{transaction_id[:8]} - Leafty"
            email_body = create_receipt_email_body(transaction_details, customer.Username)
            
            email_sent = email_service.send_email_with_attachment(
                to_email=customer.Email,
                subject=email_subject,
                body=email_body,
                attachment_content=receipt_pdf,
                attachment_filename=f"receipt_{transaction_id}.pdf"
            )
            
            if email_sent:
                logging.info(f"Receipt sent successfully to {customer.Email} for transaction {transaction_id}")
            else:
                logging.error(f"Failed to send receipt to {customer.Email} for transaction {transaction_id}")
                
        except Exception as email_error:
            logging.error(f"Error sending receipt email: {str(email_error)}")
            # Don't fail the webhook if email fails
            
        return {"message": f"Transaction {transaction_id} updated to 'On Delivery' and receipt sent to {customer.Email}"}

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Webhook processing failed: {str(e)}")


async def generate_receipt_pdf(transaction_details: dict, customer: models.User, payment_payload: InvoicePaidWebhook) -> bytes:
    """Generate a beautiful PDF receipt using the existing invoice generator"""
    
    # Validate inputs
    if not customer:
        raise ValueError("Customer object is None")
    if not transaction_details:
        raise ValueError("Transaction details are None")
    
    # Calculate totals
    subtotal = 0
    items_list = []
    
    for sub_tx in transaction_details['sub_transactions']:
        for shipment in sub_tx['market_shipments']:
            item_total = shipment['Price'] * shipment['Weight']
            subtotal += item_total
            
            items_list.append({
                "name": f"{shipment['ProductName']} (from {sub_tx['CentraUsername']})",
                "quantity": shipment['Weight'],
                "unit_cost": shipment['Price']
            })
    
    # Admin fee calculation
    admin_fee = subtotal * 0.05  # 5% admin fee
    total_amount = subtotal + admin_fee
    
    # Prepare receipt data with proper null handling
    paid_date = ""
    payment_method = "Unknown"
    
    if hasattr(payment_payload, 'paid_at') and payment_payload.paid_at:
        try:
            paid_date = pd.to_datetime(payment_payload.paid_at).strftime('%d/%m/%Y - %H:%M:%S')
        except Exception as e:
            logging.warning(f"Failed to parse paid_at date: {e}")
            paid_date = "Unknown"
    
    if hasattr(payment_payload, 'payment_method') and payment_payload.payment_method:
        payment_method = str(payment_payload.payment_method)
    
    receipt_payload = {
        "logo": encoded_logo,
        "from": "Leafty Marketplace\nJl. Kebon Jeruk No. 123\nJakarta, Indonesia\nPhone: +62-21-1234-5678\nEmail: support@leafty.com",
        "to": f"{customer.Username or 'N/A'}\n{customer.Email or 'N/A'}\nCustomer ID: {customer.UserID}",
        "number": f"RCP-{transaction_details['TransactionID'][:8]}",
        "currency": "IDR",
        "date": pd.to_datetime(transaction_details['CreatedAt']).strftime('%d/%m/%Y - %H:%M:%S'),
        "due_date": paid_date,
        "payment_terms": "Paid via Xendit",
        "items": items_list,
        "tax": 0,
        "discounts": 0,
        "shipping": admin_fee,  # Using shipping field for admin fee
        "amount_paid": total_amount,
        "notes": f"Payment Method: {payment_method}\nTransaction Status: On Delivery\nThank you for choosing Leafty!",
        "terms": "This receipt serves as proof of payment. Keep this for your records.\nFor support, contact us at support@leafty.com"
    }

    # Remove keys with None values
    receipt_payload = {k: v for k, v in receipt_payload.items() if v is not None}
    headers = {
        "Authorization": f"Bearer {INVOICE_API_KEY}"
    }

    try:
        # Send POST request to Invoice Generator API
        async with httpx.AsyncClient() as client:
            response = await client.post(INVOICE_API_URL, json=receipt_payload, headers=headers)
            
            if response.status_code == 200:
                return response.content
            else:
                raise Exception(f"Failed to generate receipt PDF. Status: {response.status_code}")
                
    except Exception as e:
        logging.error(f"Error generating receipt PDF: {str(e)}")
        raise Exception(f"Failed to generate receipt: {str(e)}")

