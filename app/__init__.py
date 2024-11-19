from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from app.extensions import db, api, jwt, cors
from config import Config
from app.error_handlers import register_error_handlers

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    db.init_app(app)
    api.init_app(app)
    jwt.init_app(app)
    cors.init_app(app)
    
    register_error_handlers(app, jwt)
    
    from app.routers.auth import auth_bp
    app.register_blueprint(auth_bp)
    
    with app.app_context():
        db.create_all()
    
    return app
    