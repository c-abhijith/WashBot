from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from app.extensions import db, api, jwt
from config import Config

def create_app():
    app = Flask(__name__)
    
    # Load config
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    api.init_app(app)
    jwt.init_app(app)
    
    # Import and register blueprints
    from app.routers.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    # Create database tables
    with app.app_context():
        db.create_all()
    
    return app
    