from flask import Flask
from flask_mail import Mail
import os
from dotenv import load_dotenv
from flask_cors import CORS 

# Load environment variables from .env file
load_dotenv()

mail = Mail()

def create_app():
    app = Flask(__name__)
    CORS(app)

    # Configuration from environment variables
    app.config['MAIL_SERVER'] = os.getenv('MAIL_SERVER', 'smtp.gmail.com')
    app.config['MAIL_PORT'] = int(os.getenv('MAIL_PORT', 587))
    app.config['MAIL_USE_TLS'] = os.getenv('MAIL_USE_TLS', 'True').lower() == 'true'
    app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
    app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
    
    # Supabase configuration
    app.config['SUPABASE_URL'] = os.getenv('SUPABASE_URL')
    app.config['SUPABASE_KEY'] = os.getenv('SUPABASE_KEY')
    
    # Print for debugging (remove in production)
    print(f"MAIL_USERNAME: {app.config['MAIL_USERNAME']}")
    print(f"SUPABASE_URL: {app.config['SUPABASE_URL']}")
    
    # Initialize extensions
    mail.init_app(app)

    # Register blueprints
    from .routes import mfa
    app.register_blueprint(mfa)

    return app