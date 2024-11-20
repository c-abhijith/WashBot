from flask import Flask
from app.extensions import db, jwt, cors
from config import Config
from app.error_handlers import register_error_handlers
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    
    # Register error handlers
    register_error_handlers(app, jwt)
    
    # Import and register blueprints
    from app.routers.auth import auth_bp
    from app.routers.user import user_bp
    from app.routers.service import service_bp
    from app.routers.vehicle import vehicle_bp
    from app.routers.booking import booking_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(service_bp)
    app.register_blueprint(vehicle_bp)
    app.register_blueprint(booking_bp)
    
    # Create database tables
    with app.app_context():
        # Import all models
        from app.models import User, Vehicle, Service, Booking, Payment
        
        # Create database directory if it doesn't exist
        db_path = os.path.dirname(app.config['SQLALCHEMY_DATABASE_URI'].replace('sqlite:///', ''))
        if db_path and not os.path.exists(db_path):
            os.makedirs(db_path)
        
        # Create tables
        db.create_all()
        
        print("Database tables created successfully!")
    
    return app
    