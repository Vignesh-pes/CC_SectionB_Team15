from flask import Blueprint, request, jsonify, current_app
from .utils import send_otp_email, store_otp, verify_otp_in_supabase
import random
import time
from functools import wraps

mfa = Blueprint('mfa', __name__)

# Simple rate limiting
rate_limit_data = {}

def rate_limit(limit=3, window=60):
    """Limit requests to 'limit' per 'window' seconds per email"""
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            data = request.json
            email = data.get('email')
            
            if email:
                current_time = time.time()
                # Initialize rate limit data for this email if needed
                if email not in rate_limit_data:
                    rate_limit_data[email] = {'count': 0, 'reset_time': current_time + window}
                
                # Reset count if window has passed
                if current_time > rate_limit_data[email]['reset_time']:
                    rate_limit_data[email] = {'count': 0, 'reset_time': current_time + window}
                
                # Increment count
                rate_limit_data[email]['count'] += 1
                
                # Check if count exceeds limit
                if rate_limit_data[email]['count'] > limit:
                    wait_time = int(rate_limit_data[email]['reset_time'] - current_time)
                    return jsonify({
                        'error': f'Rate limit exceeded. Please try again in {wait_time} seconds'
                    }), 429
            
            return f(*args, **kwargs)
        return decorated_function
    return decorator

@mfa.route('/generate-otp', methods=['POST'])
@rate_limit(limit=3, window=60)
def generate_otp():
    data = request.json
    email = data.get('email')

    if not email:
        return jsonify({'error': 'Email is required'}), 400

    otp = str(random.randint(100000, 999999))
    try:
        store_otp(email, otp)
        send_otp_email(email, otp)
    except Exception as e:
        return jsonify({'error': f'Failed to send OTP: {str(e)}'}), 500

    return jsonify({'message': 'OTP sent successfully'}), 200

@mfa.route('/verify-otp', methods=['POST'])
@rate_limit(limit=5, window=60)
def verify_otp():
    data = request.json
    email = data.get('email')
    otp = data.get('otp')

    if not email or not otp:
        return jsonify({'error': 'Email and OTP are required'}), 400

    try:
        if verify_otp_in_supabase(email, otp):
            return jsonify({'message': 'OTP verified successfully'}), 200
        else:
            return jsonify({'error': 'Invalid or expired OTP'}), 401
    except Exception as e:
        return jsonify({'error': f'Verification failed: {str(e)}'}), 500