import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.image import MIMEImage
from email import encoders
import os
import base64
from typing import Optional
import logging
from datetime import datetime

# Load and encode the LeaftyLogo.png
def get_encoded_logo():
    try:
        # Use LeaftyLogo.png for simplicity and compatibility
        with open("./LeaftyLogo.png", "rb") as logo_file:
            return base64.b64encode(logo_file.read()).decode('utf-8')
    except FileNotFoundError:
        logging.error("LeaftyLogo.png not found")
        return None

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        self.smtp_port = int(os.getenv("SMTP_PORT", "587"))
        self.email_address = os.getenv("EMAIL")
        self.email_password = os.getenv("PASSWORD")
        
    def send_email_with_attachment(
        self, 
        to_email: str, 
        subject: str, 
        body: str, 
        attachment_content: bytes, 
        attachment_filename: str,
        attachment_type: str = "application/pdf",
        embed_logo: bool = True
    ) -> bool:
        """Send email with PDF attachment and optional embedded logo"""
        try:
            # Validate inputs
            if not to_email or not subject or not body:
                logging.error("Missing required email parameters")
                return False
                
            if not attachment_content:
                logging.error("Attachment content is empty")
                return False
                
            # Create message - use 'related' for embedded images
            msg = MIMEMultipart('related')
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject

            # Create the HTML part
            msg_html = MIMEMultipart('alternative')
            
            # Add HTML body to email
            html_part = MIMEText(body, 'html')
            msg_html.attach(html_part)
            
            # Attach the HTML part to the main message
            msg.attach(msg_html)

            # Embed logo if requested
            if embed_logo:
                try:
                    # Use LeaftyLogo.png for simplicity and compatibility
                    logo_path = "./LeaftyLogo.png"
                    
                    if os.path.exists(logo_path):
                        with open(logo_path, 'rb') as logo_file:
                            logo_data = logo_file.read()
                            # Use MIMEImage for PNG - much simpler than SVG
                            logo_image = MIMEImage(logo_data)
                            logo_image.add_header('Content-ID', '<leafty_logo>')
                            logo_image.add_header('Content-Disposition', 'inline', filename='leafty_logo.png')
                            msg.attach(logo_image)
                            logging.info(f"PNG logo embedded successfully from {logo_path}")
                    else:
                        logging.warning("LeaftyLogo.png file not found for embedding")
                except Exception as e:
                    logging.error(f"Failed to embed PNG logo: {str(e)}")

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
            
            # Validate credentials before login
            if not self.email_address or not self.email_password:
                raise ValueError("Email credentials are not properly configured")
                
            server.login(self.email_address, self.email_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.email_address, to_email, text)
            server.quit()
            
            logging.info(f"Receipt email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logging.error(f"SMTP Authentication failed: {str(e)}")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            logging.error(f"Invalid recipient email {to_email}: {str(e)}")
            return False
        except smtplib.SMTPException as e:
            logging.error(f"SMTP error occurred: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

    def send_simple_email(self, to_email: str, subject: str, body: str, embed_logo: bool = True, logo_filename: str = "LeaftyLogo.png") -> bool:
        """Send simple HTML email without attachment but with optional embedded logo"""
        try:
            # Validate inputs
            if not to_email or not subject or not body:
                logging.error("Missing required email parameters")
                return False
            
            # Create message
            msg = MIMEMultipart('related')  # Use 'related' for embedded images
            msg['From'] = self.email_address
            msg['To'] = to_email
            msg['Subject'] = subject

            # Create the HTML part
            msg_html = MIMEMultipart('alternative')
            
            # Add HTML body to email
            html_part = MIMEText(body, 'html')
            msg_html.attach(html_part)
            
            # Attach the HTML part to the main message
            msg.attach(msg_html)
            
            # Embed logo if requested
            if embed_logo:
                try:
                    # Use configurable logo filename
                    logo_path = f"./{logo_filename}"
                    
                    if os.path.exists(logo_path):
                        with open(logo_path, 'rb') as logo_file:
                            logo_data = logo_file.read()
                            # Use MIMEImage for PNG - much simpler than SVG
                            logo_image = MIMEImage(logo_data)
                            logo_image.add_header('Content-ID', '<leafty_logo>')
                            logo_image.add_header('Content-Disposition', f'inline', filename='leafty_logo.png')
                            msg.attach(logo_image)
                            logging.info(f"PNG logo embedded successfully from {logo_path}")
                    else:
                        logging.warning(f"{logo_filename} file not found for embedding")
                except Exception as e:
                    logging.error(f"Failed to embed PNG logo: {str(e)}")

            # Create SMTP session
            server = smtplib.SMTP(self.smtp_server, self.smtp_port)
            server.starttls()  # Enable security
            
            # Validate credentials before login
            if not self.email_address or not self.email_password:
                raise ValueError("Email credentials are not properly configured")
                
            server.login(self.email_address, self.email_password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.email_address, to_email, text)
            server.quit()
            
            logging.info(f"Email sent successfully to {to_email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logging.error(f"SMTP Authentication failed: {str(e)}")
            return False
        except smtplib.SMTPRecipientsRefused as e:
            logging.error(f"Invalid recipient email {to_email}: {str(e)}")
            return False
        except smtplib.SMTPException as e:
            logging.error(f"SMTP error occurred: {str(e)}")
            return False
        except Exception as e:
            logging.error(f"Failed to send email to {to_email}: {str(e)}")
            return False

def create_otp_email_body(otp_code: str, user_email: str, expiry_minutes: int = 10) -> str:
    """Create OTP verification email body matching the provided design"""
    
    # Split OTP code into individual digits
    otp_digits = list(str(otp_code).zfill(6))  # Ensure 6 digits
    
    html_body = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>OTP Verification - Leafty</title>
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@500;600&display=swap');
            * {{
                font-family: 'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
            }}
        </style>
    </head>
    <body style="margin: 0; padding: 0; font-family: 'Montserrat', sans-serif; background-color: #F7FAFC;">
        <table width="100%" cellpadding="0" cellspacing="0" border="0" style="background-color: #F7FAFC; padding: 56px 54px; font-family: 'Montserrat', sans-serif;">
            <tr>
                <td align="center">
                    <table width="574.78" cellpadding="10" cellspacing="0" border="0" style="max-width: 574.78px; background-color: #F7FAFC; font-family: 'Montserrat', sans-serif;">
                        <tr>
                            <td align="center">
                                <!-- Logo -->
                                <img src="cid:leafty_logo" alt="Leafty Logo" style="width: 292px; height: 91px; display: block; margin-bottom: 30px;" />
                                
                                <!-- Title -->
                                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-bottom: 24px; font-family: 'Montserrat', sans-serif;">
                                    <tr>
                                        <td align="center">
                                            <div style="width: 419px; text-align: center; color: black; font-size: 32px; font-family: 'Montserrat', sans-serif; font-weight: 600; letter-spacing: 0.64px; margin-bottom: 16px;">
                                                OTP Verification
                                            </div>
                                            <div style="width: 419px; text-align: center; color: #606060; font-size: 20px; font-family: 'Montserrat', sans-serif; font-weight: 500; letter-spacing: 0.40px; line-height: 1.5;">
                                                Use this code to sign up to Leafty.<br/>
                                                This code will expire in {expiry_minutes} minutes
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- OTP Code -->
                                <table cellpadding="0" cellspacing="0" border="0" align="center" style="background: #DCEFEF; border-radius: 10px; margin: 40px auto; user-select: all; -webkit-user-select: all; -moz-user-select: all; font-family: 'Montserrat', sans-serif;">
                                    <tr>
                                        <td style="width: 81.39px; padding: 16.61px;">
                                            <div style="text-align: center; color: black; font-size: 42px; font-family: 'Montserrat', sans-serif; font-weight: 600; letter-spacing: 0.84px; user-select: text; -webkit-user-select: text; -moz-user-select: text;">{otp_digits[0]}</div>
                                        </td>
                                        <td style="width: 81.39px; padding: 16.61px;">
                                            <div style="text-align: center; color: black; font-size: 42px; font-family: 'Montserrat', sans-serif; font-weight: 600; letter-spacing: 0.84px; user-select: text; -webkit-user-select: text; -moz-user-select: text;">{otp_digits[1]}</div>
                                        </td>
                                        <td style="width: 81.39px; padding: 16.61px;">
                                            <div style="text-align: center; color: black; font-size: 42px; font-family: 'Montserrat', sans-serif; font-weight: 600; letter-spacing: 0.84px; user-select: text; -webkit-user-select: text; -moz-user-select: text;">{otp_digits[2]}</div>
                                        </td>
                                        <td style="width: 81.39px; padding: 16.61px;">
                                            <div style="text-align: center; color: black; font-size: 42px; font-family: 'Montserrat', sans-serif; font-weight: 600; letter-spacing: 0.84px; user-select: text; -webkit-user-select: text; -moz-user-select: text;">{otp_digits[3]}</div>
                                        </td>
                                        <td style="width: 81.39px; padding: 16.61px;">
                                            <div style="text-align: center; color: black; font-size: 42px; font-family: 'Montserrat', sans-serif; font-weight: 600; letter-spacing: 0.84px; user-select: text; -webkit-user-select: text; -moz-user-select: text;">{otp_digits[4]}</div>
                                        </td>
                                        <td style="width: 81.39px; padding: 16.61px;">
                                            <div style="text-align: center; color: black; font-size: 42px; font-family: 'Montserrat', sans-serif; font-weight: 600; letter-spacing: 0.84px; user-select: text; -webkit-user-select: text; -moz-user-select: text;">{otp_digits[5]}</div>
                                        </td>
                                    </tr>
                                </table>
                                
                                <!-- Email Info -->
                                <table width="100%" cellpadding="0" cellspacing="0" border="0" style="margin-top: 40px; font-family: 'Montserrat', sans-serif;">
                                    <tr>
                                        <td align="center">
                                            <div style="width: 435px; text-align: center; margin-bottom: 40px; font-family: 'Montserrat', sans-serif;">
                                                <span style="color: #606060; font-size: 20px; font-family: 'Montserrat', sans-serif; font-weight: 500; letter-spacing: 0.40px;">
                                                    This code will securely sign you up using<br/>
                                                </span>
                                                <span style="color: #0F7275; font-size: 20px; font-family: 'Montserrat', sans-serif; font-weight: 500; letter-spacing: 0.40px; pointer-events: none; cursor: default;">
                                                    {user_email}
                                                </span>
                                            </div>
                                        </td>
                                    </tr>
                                    <tr>
                                        <td align="center">
                                            <div style="width: 435px; text-align: center; color: #B0B0B0; font-size: 14px; font-family: 'Montserrat', sans-serif; font-weight: 500; letter-spacing: 0.28px;">
                                                If you didn't request this email, you can ignore it
                                            </div>
                                        </td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                </td>
            </tr>
        </table>
    </body>
    </html>
    """
    
    return html_body

def create_receipt_email_body(transaction_data: dict, customer_name: str) -> str:
    """Create a beautiful HTML email body for the receipt"""
    
    # Create logo with embedded CID reference and fallback
    logo_html = '''
    <div style="background-color: white; width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 20px; display: flex; align-items: center; justify-content: center; position: relative;">
        <img src="cid:leafty_logo" alt="Leafty Logo" style="width: 60px; height: 60px; border-radius: 50%;" 
             onerror="this.style.display='none'; this.nextElementSibling.style.display='flex';" />
        <div style="display: none; width: 50px; height: 50px; background: linear-gradient(135deg, #0F7275 0%, #79B2B7 100%); border-radius: 50%; align-items: center; justify-content: center; color: white; font-size: 20px; font-weight: bold;">L</div>
    </div>
    '''
    
    # Calculate totals - MUST match invoice PDF exactly
    subtotal = 0
    total_items = 0
    total_savings = 0
    
    for sub_tx in transaction_data['sub_transactions']:
        for shipment in sub_tx['market_shipments']:
            # Calculate subtotal based on InitialPrice (before discount)
            initial_price = shipment.get('InitialPrice', shipment['Price'])
            item_total = initial_price * shipment['Weight']
            subtotal += item_total
            
            # Calculate discount savings
            if initial_price != shipment['Price']:
                discount_amount = (initial_price - shipment['Price']) * shipment['Weight']
                total_savings += discount_amount
            
            total_items += 1
    
    # Fixed fees (consistent with invoice PDF)
    admin_fee = 5000
    shipping_fee = 50000
    total_amount = subtotal + admin_fee + shipping_fee - total_savings
    
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
                {logo_html}
                <h1 style="color: white; margin: 0; font-size: 28px; font-weight: 700;">Payment Successful!</h1>
                <p style="color: rgba(255,255,255,0.9); margin: 10px 0 0; font-size: 16px;">Thank you for your purchase</p>
            </div>
            
            <!-- Transaction Info -->
            <div style="padding: 30px;">
                <div style="background-color: #f8fffe; border-radius: 8px; padding: 20px; margin-bottom: 25px; border-left: 4px solid #79B2B7;">
                    <h2 style="color: #0F7275; margin: 0 0 15px; font-size: 20px;">Transaction Details</h2>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #666; font-weight: 500;">Transaction ID: </span>
                        <span style="color: #333; font-weight: 600;">{transaction_data['TransactionID']}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #666; font-weight: 500;">Date: </span>
                        <span style="color: #333; font-weight: 600;">{datetime.fromisoformat(transaction_data['CreatedAt'].replace('Z', '+00:00')).strftime('%B %d, %Y at %I:%M %p')}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                        <span style="color: #666; font-weight: 500;">Customer: </span>
                        <span style="color: #333; font-weight: 600;">{customer_name}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #666; font-weight: 500;">Supplier(s): </span>
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
                        <span style="color: #666; font-size: 16px;">Subtotal ({total_items} items): </span>
                        <span style="color: #333; font-size: 16px; font-weight: 600;">Rp {subtotal:,}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="color: #666; font-size: 16px;">Admin Fee: </span>
                        <span style="color: #333; font-size: 16px; font-weight: 600;">Rp {admin_fee:,}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                        <span style="color: #666; font-size: 16px;">Shipping Fee: </span>
                        <span style="color: #333; font-size: 16px; font-weight: 600;">Rp {shipping_fee:,}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between; margin-bottom: 15px; padding-bottom: 15px; border-bottom: 1px solid #ddd;">
                        <span style="color: #E67E22; font-size: 16px;">Discount Savings: </span>
                        <span style="color: #27AE60; font-size: 16px; font-weight: 600;">- Rp {total_savings:,}</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: #0F7275; font-size: 20px; font-weight: 700;">Total Amount: </span>
                        <span style="color: #0F7275; font-size: 20px; font-weight: 700;">Rp {total_amount:,}</span>
                    </div>
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

def send_otp_email(to_email: str, otp_code: str, expiry_minutes: int = 10) -> bool:
    """Convenience function to send OTP email with FullLeaftyLogo.png"""
    email_service = EmailService()
    subject = "Your OTP Code - Leafty Verification"
    body = create_otp_email_body(otp_code, to_email, expiry_minutes)
    
    return email_service.send_simple_email(to_email, subject, body, embed_logo=True, logo_filename="FullLeaftyLogo.png")