from flask import Blueprint, request
from flask_restful import Resource, Api
from app.models import User
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middleware.auth_middleware import admin_required
import uuid

user_bp = Blueprint('user', __name__)
api = Api(user_bp)

class CurrentUser(Resource):
    @jwt_required()
    def get(self):
        """Get current user details from token"""
        try:
            current_user_id = get_jwt_identity()
            user_uuid = uuid.UUID(current_user_id)
            user = User.query.filter_by(id=user_uuid).first()
            
            if not user:
                return {"message": "User not found"}, 404
            
            return {
                "message": "User retrieved successfully",
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "role": user.role,
                    "phonenumber": user.phonenumber,
                    "profile_image": user.profile_image
                }
            }, 200
            
        except ValueError:
            return {"message": "Invalid user ID format"}, 400
        except Exception as error:
            return {
                "message": "An error occurred while fetching user",
                "error": str(error)
            }, 500

class UserList(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """Get list of all users (admin only)"""
        try:
            users = User.query.all()
            users_data = [{
                "id": str(user.id),
                "username": user.username,
                "role": user.role,
                "phonenumber": user.phonenumber,
                "profile_image": user.profile_image
            } for user in users]
            
            return {
                "message": "Users retrieved successfully",
                "users": users_data,
                "total": len(users_data)
            }, 200
            
        except Exception as error:
            return {
                "message": "An error occurred while fetching users",
                "error": str(error)
            }, 500

# Register routes
api.add_resource(CurrentUser, '/user')  # Get current user from token
api.add_resource(UserList, '/user_list')  # Admin only - list all users 