from flask import Flask
from app.extensions import db, jwt, cors
from config import Config
from app.error_handlers import register_error_handlers
from app.models import User, Service

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
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
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(service_bp)
    
    return app
    