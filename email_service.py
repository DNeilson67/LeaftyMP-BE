import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from typing import Optional
import logging
from datetime import datetime

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_address = os.getenv("EMAIL_ADDRESS")
        self.email_password = os.getenv("EMAIL_PASSWORD")
        
    def send_email_with_attachment(
        self, 
        to_email: str, 
        subject: str, 
        body: str, 
        attachment_content: bytes, 
        attachment_filename: str,
        attachment_type: str = "application/pdf"
    ) -> bool:
        """Send email with PDF attachment"""
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject

            # Add body to email
            msg.attach(MIMEText(body, 'html'))

            # Add attachment
            attachment = MIMEBase('application', 'octet-stream')
            attachment.set_payload(attachment_content)
            encoders.encode_base64(attachment)
            attachment.add_header(
                'Content-Disposition',
                f'attachment; filename= {attachment_filename}'
            )
            msg.attach(attachment)

            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable security
            server.login(self.email_address, self.email_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.email_address, to_email, text)
            server.quit()
            
            logging.info(f"Receipt email sent successfully to {to_email}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

def create_receipt_email_body(transaction_data: dict, customer_name: str) -> str:
    """Create a beautiful HTML email body for the receipt"""
    
    # Calculate totals
    subtotal = 0
    total_items = 0
    
    for sub_tx in transaction_data['sub_transactions']:
        for shipment in sub_tx['market_shipments']:
            subtotal += shipment['Price'] * shipment['Weight']
            total_items += 1
    
    # Admin fee (if applicable)
    admin_fee = subtotal * 0.05  # 5% admin fee example
    total_amount = subtotal + admin_fee
    
    # Create items list HTML
    items_html = ""
    for sub_tx in transaction_data['sub_transactions']:
        for shipment in sub_tx['market_shipments']:
            item_total = shipment['Price'] * shipment['Weight']
            items_html += f"""
            <tr style="border-bottom: 1px solid #eee;">
                <td style="padding: 12px; color: #555;">{shipment['ProductName']}</td>
                <td style="padding: 12px; color: #555; text-align: center;">{shipment['Weight']} kg</td>
                <td style="padding: 12px; color: #555; text-align: right;">Rp {shipment['Price']:,}</td>
                <td style="padding: 12px; color: #555; text-align: right; font-weight: 600;">Rp {item_total:,}</td>
            </tr>
            """
    
    # Create centras list
    centras_list = []
    for sub_tx in transaction_data['sub_transactions']:
        if sub_tx['CentraUsername'] not in centras_list:
            centras_list.append(sub_tx['CentraUsername'])
    
    centras_text = ", ".join(centras_list) if len(centras_list) <= 2 else f"{centras_list[0]}, {centras_list[1]} and {len(centras_list)-2} others"
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Transaction Receipt - Leafty</title>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; background-color: #f8fffe;">
        <div style="max-width: 600px; margin: 20px auto; background-color: white; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);">
            
            <!-- Header -->
            <div style="background: linear-gradient(135deg, #0F7275 0%, #79B2B7 100%); padding: 30px; text-align: center;">
                <div style="background-color: white; width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center;">
                    <svg width="50" height="50" viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
                        <path d="M12 2L13.09 8.26L20 9L13.09 9.74L12 16L10.91 9.74L4 9L10.91 8.26L12 2Z" fill="#0F7275"/>
                    </svg>
                </div>
                <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 700;">Payment Successful!</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0; font-size: 16px;">Thank you for your purchase</p>
            </div>
            
            <!-- Transaction Info -->
            <div style="padding: 30px;">
                <div style="background-color: #f8fffe; border-radius: 8px; padding: 20px; margin-bottom: 25px; border-left: 4px solid #79B2B7;">
                    <h2 style="color: #0F7275; margin: 0 0 15px; font-size: 20px;">Transaction Details</h2>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #666; font-weight: 500;">Transaction ID:</span>
                        <span style="color: #333; font-weight: 600; font-family: monospace;">{transaction_data['TransactionID']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #666; font-weight: 500;">Date:</span>
                        <span style="color: #333; font-weight: 600;">{datetime.fromisoformat(transaction_data['CreatedAt'].replace('Z', '+00:00')).strftime('%B %d, %Y at %I:%M %p')}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #666; font-weight: 500;">Customer:</span>
                        <span style="color: #333; font-weight: 600;">{customer_name}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #666; font-weight: 500;">Supplier(s):</span>
                        <span style="color: #333; font-weight: 600;">{centras_text}</span>
                    </div>
                </div>
                
                <!-- Items Table -->
                <h3 style="color: #0F7275; margin: 0 0 15px; font-size: 18px;">Order Summary</h3>
                <div style="overflow-x: auto; margin-bottom: 20px;">
                    <table style="width: 100%; border-collapse: collapse; background-color: white; border-radius: 8px; overflow: hidden; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">
                        <thead>
                            <tr style="background-color: #0F7275;">
                                <th style="padding: 15px; text-align: left; color: white; font-weight: 600;">Product</th>
                                <th style="padding: 15px; text-align: center; color: white; font-weight: 600;">Quantity</th>
                                <th style="padding: 15px; text-align: right; color: white; font-weight: 600;">Unit Price</th>
                                <th style="padding: 15px; text-align: right; color: white; font-weight: 600;">Total</th>
                            </tr>
                        </thead>
                        <tbody>
                            {items_html}
                        </tbody>
                    </table>
                </div>
                
                <!-- Totals -->
                <div style="background-color: #f8fffe; border-radius: 8px; padding: 20px;">
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="color: #666; font-size: 16px;">Subtotal ({total_items} items):</span>
                        <span style="color: #333; font-size: 16px; font-weight: 600;">Rp {subtotal:,}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #ddd;">
                        <span style="color: #666; font-size: 16px;">Admin Fee (5%):</span>
                        <span style="color: #333; font-size: 16px; font-weight: 600;">Rp {admin_fee:,}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #0F7275; font-size: 20px; font-weight: 700;">Total Amount:</span>
                        <span style="color: #0F7275; font-size: 20px; font-weight: 700;">Rp {total_amount:,}</span>
                    </div>
                </div>
                
                <!-- Status -->
                <div style="text-align: center; margin-top: 30px; padding: 20px; background: linear-gradient(135deg, #C0CD30 0%, #94C3B3 100%); border-radius: 8px;">
                    <h3 style="color: white; margin: 0 0 10px; font-size: 18px;">Order Status</h3>
                    <div style="background-color: rgba(255,255,255,0.2); color: white; padding: 10px 20px; border-radius: 20px; display: inline-block; font-weight: 600;">
                        🚚 On Delivery
                    </div>
                    <p style="color: rgba(255,255,255,0.9); margin: 15px 0 0; font-size: 14px;">
                        Your order is being prepared and will be shipped soon. You'll receive tracking information via email.
                    </p>
                </div>
                
                <!-- Footer -->
                <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 1px solid #eee;">
                    <p style="color: #666; font-size: 14px; margin: 0 0 10px;">
                        Questions about your order? Contact our support team at 
                        <a href="mailto:support@leafty.com" style="color: #0F7275; text-decoration: none;">support@leafty.com</a>
                    </p>
                    <p style="color: #999; font-size: 12px; margin: 0;">
                        This is an automated email. Please do not reply to this message.
                    </p>
                </div>
            </div>
        </div>
    </body>
    </html>
    """
    
    return html_body