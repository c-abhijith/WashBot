from flask import Blueprint, request
from flask_restful import Resource, Api
from app.helper.body_validator import check_signup, check_login
from app.models import User
from app.extensions import db
from app.helper.auth_helper import password_hash, access_token, refres_token
from flask_jwt_extended import jwt_required, get_jwt_identity, get_jwt
from app.response import success_response,server_response
auth_bp = Blueprint('auth', __name__)
api = Api(auth_bp)

BLOCKLIST = set()

class Signup(Resource):
    def post(self):
        try:
            data = request.get_json()
            signup_check = check_signup(data)
            if signup_check:
                return signup_check
            try:
                hashed_password = password_hash(data["password"])
                new_user = User(
                    username=data["username"],
                    phonenumber=data["phonenumber"],
                    password=hashed_password, 
                    role=data["role"]
                )
                
                db.session.add(new_user)
                db.session.commit()
                return success_response.signup_response(new_user), 201
                
            except Exception as db_error:
                db.session.rollback()
                return server_response.data_error(db_error) , 500
            
        except Exception as error:
            return server_response.unexcept_error, 500

class Login(Resource):
    def post(self):
        try:
            data = request.get_json()
            login_check = check_login(data)
            if login_check:
                return login_check
            
            user = User.query.filter_by(username=data["username"]).first()

            access_token_str = access_token(user)
            refresh_token_str = refres_token(user)
            
            return success_response.login_response(access_token_str,refresh_token_str), 200
        except Exception as error:
            return server_response.unexcept_error(error), 500

class Logout(Resource):
    @jwt_required()
    def post(self):
        try:
            jti = get_jwt()["jti"]  
            BLOCKLIST.add(jti)
            return {"message": "Successfully logged out"}, 200
        except Exception as error:
            return server_response.unexcept_error(error), 500

class LogoutRefresh(Resource):
    @jwt_required(refresh=True)
    def post(self):
        try:
            jti = get_jwt()["jti"] 
            BLOCKLIST.add(jti)
            return {"message": "Refresh token revoked"}, 200
        except Exception as error:
            return server_response.unexcept_error(error), 500
        
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
            return server_response.unexcept_error(error), 500

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