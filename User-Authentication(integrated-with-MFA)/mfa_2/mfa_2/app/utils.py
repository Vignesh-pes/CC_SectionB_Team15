from flask_mail import Message
from . import mail
from supabase import create_client
from flask import current_app
import datetime
import os

def send_otp_email(email, otp):
    msg = Message('Your OTP Code', sender=current_app.config['MAIL_USERNAME'], recipients=[email])
    msg.body = f'Your OTP is: {otp}'
    mail.send(msg)

def get_supabase_client():
    # Try to get from current_app first
    url = current_app.config.get('SUPABASE_URL')
    key = current_app.config.get('SUPABASE_KEY')
    
    # If not found, try environment variables
    if not url or not key:
        url = os.getenv("SUPABASE_URL")
        key = os.getenv("SUPABASE_KEY")
        
    # Print for debugging (remove in production)
    print(f"SUPABASE_URL found: {'Yes' if url else 'No'}")
    print(f"SUPABASE_KEY found: {'Yes' if key else 'No'}")
    
    if not url or not key:
        raise Exception("Supabase URL or Key not found in environment variables")
    return create_client(url, key)

def store_otp(email, otp):
    supabase = get_supabase_client()
    # First, delete any existing OTPs for this email
    clean_old_otps(email)
    
    # Then store the new OTP
    supabase.table('otp_table').insert({
        'email': email,
        'otp': otp,
        'created_at': datetime.datetime.utcnow().isoformat()
    }).execute()

def clean_old_otps(email):
    """Remove all previous OTPs for this email"""
    supabase = get_supabase_client()
    supabase.table('otp_table').delete().eq('email', email).execute()

def verify_otp_in_supabase(email, otp):
    supabase = get_supabase_client()
    current_time = datetime.datetime.utcnow()
    expiration_time = current_time - datetime.timedelta(minutes=10)  # 10-minute expiration
    
    result = supabase.table('otp_table').select("*")\
        .eq('email', email)\
        .eq('otp', otp)\
        .gte('created_at', expiration_time.isoformat())\
        .execute()
    
    # If OTP is valid, clean it up
    if len(result.data) > 0:
        clean_old_otps(email)
        
    return len(result.data) > 0