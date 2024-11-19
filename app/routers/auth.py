from flask import Blueprint, request
from flask_restful import Resource, Api
from app.helper.body_validator import check_signup, check_login
from app.models import User
from app.extensions import db
from app.helper.auth_helper import password_hash, verify_password,access_token,refres_token
from flask_jwt_extended import jwt_required, get_jwt_identity


auth_bp = Blueprint('auth', __name__)
api = Api(auth_bp)

class Signup(Resource):
    def post(self):
        try:
            data = request.get_json()
            signup_check = check_signup(data)
            if signup_check:
                return signup_check
            
            
            if User.query.filter_by(username=data["username"]).first():
                return {"message": "Username already exists"}, 400
                
            hashed_password = password_hash(data["password"])
            
            new_user = User(
                username=data["username"],
                phonenumber=data["phonenumber"],
                password=hashed_password, 
                role=data["role"]
            )
            db.session.add(new_user)
            db.session.commit()
            return {"message": "User created", "id": str(new_user.id)}, 201
        except Exception as error:
            return {"message": "An error occurred while creating the user",
                    "error": str(error)}, 500

class Login(Resource):
    def post(self):
        try:
            data = request.get_json()
            login_check = check_login(data)
            if login_check:
                return login_check
            
            user = User.query.filter_by(username=data["username"]).first()
            
            if not user or not verify_password(data["password"], user.password):
                return {"message": "Invalid username or password"}, 401

            accessh_token = access_token(user)
            refresh_token = refres_token(user)
            
            return {
                "message": "Login successful",
                "access_token": accessh_token,
                "refresh_token": refresh_token,
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "role": user.role
                }
            }, 200
        except Exception as error:
            return {"message": "An error occurred during login",
                    "error": str(error)}, 500

class RefreshToken(Resource):
    @jwt_required(refresh=True)
    def post(self):
        try:
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)
            
            if not user:
                return {"message": "User not found"}, 404
            
            accessh_token = access_token(user)
            
            return {
                "access_token": accessh_token,
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


api.add_resource(Signup, '/signup')
api.add_resource(Login, '/login')
api.add_resource(RefreshToken, '/refresh')
api.add_resource(ProtectedRoute, '/protected')