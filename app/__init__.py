from flask import Flask
from app.extensions import db, jwt, cors
from config import Config
from app.error_handlers import register_error_handlers
from app.routers.auth import BLOCKLIST

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    
    # JWT configuration
    @jwt.token_in_blocklist_loader
    def check_if_token_in_blocklist(jwt_header, jwt_payload):
        return jwt_payload["jti"] in BLOCKLIST
        
    @jwt.revoked_token_loader
    def revoked_token_callback(jwt_header, jwt_payload):
        return {
            "message": "The token has been revoked",
            "error": "token_revoked"
        }, 401
    
    # Register error handlers
    register_error_handlers(app, jwt)
    
    # Import and register blueprints
    from app.routers.auth import auth_bp
    from app.routers.user import user_bp
    
    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    
    with app.app_context():
        db.create_all()
    
    return app
    