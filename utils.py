import os
from datetime import datetime, timedelta
from functools import wraps
from flask import abort
from flask_login import current_user
import random
import string
from twilio.rest import Client

# Twilio configuration
TWILIO_ACCOUNT_SID = os.environ.get('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = os.environ.get('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = os.environ.get('TWILIO_PHONE_NUMBER')

client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)

def calculate_price(weight, number_of_bags, trolley_required):
    """Calculate the total price based on weight, number of bags, and trolley requirement"""
    # Base price: Rs. 5 per kg
    base_price = weight * 5
    
    # Additional charge for number of bags: Rs. 10 per bag
    bag_charge = number_of_bags * 10
    
    # Trolley charge: Rs. 200 if required
    trolley_charge = 200 if trolley_required else 0
    
    # Minimum charge: Rs. 100
    total = base_price + bag_charge + trolley_charge
    return max(total, 100)

def admin_required(f):
    """Decorator to check if user is admin"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def porter_required(f):
    """Decorator to check if user is porter"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'porter':
            abort(403)
        return f(*args, **kwargs)
    return decorated_function

def format_currency(amount):
    """Format amount in Indian Rupees"""
    return f"₹{amount:.2f}"

def generate_pdf_pass(booking):
    """Generate PDF pass for booking"""
    # Implementation using WeasyPrint would go here
    pass

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def send_otp_sms(phone_number, otp):
    """Send OTP via SMS using Twilio"""
    try:
        message = client.messages.create(
            body=f'Your PorterPro booking verification code is: {otp}. Valid for 10 minutes.',
            from_=TWILIO_PHONE_NUMBER,
            to=phone_number
        )
        return True
    except Exception as e:
        print(f"Error sending SMS: {str(e)}")
        return False

def verify_otp(booking, otp):
    """Verify OTP for a booking"""
    if not booking.otp or not booking.otp_expiry:
        return False
    
    if datetime.utcnow() > booking.otp_expiry:
        return False
    
    return booking.otp == otp
