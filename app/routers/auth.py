from flask import Blueprint, request
from flask_restful import Resource, Api
from app.helper.body_validator import check_signup, check_login
from app.models import User
from app.extensions import db
from app.helper.auth_helper import password_hash, verify_password, access_token, refres_token
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt

auth_bp = Blueprint('auth', __name__)
api = Api(auth_bp)

# Create a blocklist set to store revoked tokens
# In production, use Redis or database instead of in-memory set
BLOCKLIST = set()

class Signup(Resource):
    def post(self):
        try:
            data = request.get_json()
            
            # Validate input data
            signup_check = check_signup(data)
            if signup_check:
                return signup_check
            
            # Check for existing user
            existing_user = User.query.filter_by(username=data["username"]).first()
            if existing_user:
                return {"message": "Username already exists"}, 400
                
            try:
                # Hash password
                hashed_password = password_hash(data["password"])
                
                # Create new user
                new_user = User(
                    username=data["username"],
                    phonenumber=data["phonenumber"],
                    password=hashed_password, 
                    role=data["role"]
                )
                
                # Save to database
                db.session.add(new_user)
                db.session.commit()
                
                # Prepare response
                response_data = {
                    "message": "User created", 
                    "user": {
                        "id": str(new_user.id),
                        "username": new_user.username,
                        "role": new_user.role,
                        "phonenumber": new_user.phonenumber
                    }
                }
                
                return response_data, 201
                
            except Exception as db_error:
                db.session.rollback()
                return {
                    "message": "Database error occurred",
                    "error": str(db_error)
                }, 500
            
        except Exception as error:
            return {
                "message": "An unexpected error occurred",
                "error": str(error)
            }, 500

class Login(Resource):
    def post(self):
        try:
            data = request.get_json()
            login_check = check_login(data)
            if login_check:
                return login_check
            
            user = User.query.filter_by(username=data["username"]).first()
            if not user:
                return {"message": "Invalid username"}, 401
            
            if not verify_password(data["password"], user.password):
                return {"message": "Invalid password"}, 401

            access_token_str = access_token(user)
            refresh_token_str = refres_token(user)
            
            return {
                "message": "Login successful",
                "access_token": access_token_str,
                "refresh_token": refresh_token_str,
                "user": user.to_dict()
            }, 200
        except Exception as error:
            return {"message": "An error occurred during login",
                    "error": str(error)}, 500

class Logout(Resource):
    @jwt_required()
    def post(self):
        try:
            jti = get_jwt()["jti"]  # Get JWT ID
            BLOCKLIST.add(jti)
            return {"message": "Successfully logged out"}, 200
        except Exception as error:
            return {
                "message": "An error occurred during logout",
                "error": str(error)
            }, 500

class LogoutRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        try:
            jti = get_jwt()["jti"]  # Get JWT ID
            BLOCKLIST.add(jti)
            return {"message": "Refresh token revoked"}, 200
        except Exception as error:
            return {
                "message": "An error occurred during refresh token revocation",
                "error": str(error)
            }, 500

class RefreshToken(Resource):
    @jwt_required(refresh=True)
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return {"message": "User not found"}, 404
            
            access_token_str = access_token(user)
            
            return {
                "access_token": access_token_str,
                "message": "Token refreshed successfully"
            }, 200
        except Exception as error:
            return {"message": "Error refreshing token",
                    "error": str(error)}, 500

class ProtectedRoute(Resource):
    @jwt_required()
    def get(self):
        current_user_id = get_jwt_identity()
        return {"logged_in_as": current_user_id}, 200

# Register routes
api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(Logout, '/logout')
api.add_resource(LogoutRefresh, '/logout-refresh')
api.add_resource(RefreshToken, '/refresh')
api.add_resource(ProtectedRoute, '/protected')