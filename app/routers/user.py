from flask import Blueprint, request, current_app
from flask_restful import Resource, Api
from app.models import User
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middleware.auth_middleware import admin_required
from app.helper.cloudinary_helper import upload_image, delete_image
import uuid

user_bp = Blueprint('user', __name__)
api = Api(user_bp)

class UserProfile(Resource):
    @jwt_required()
    def get(self):
        """Get current user profile"""
        try:
            current_user_id = get_jwt_identity()
            user_uuid = uuid.UUID(current_user_id)
            user = User.query.filter_by(id=user_uuid).first()
            
            if not user:
                return {"message": "User not found"}, 404
            
            return {
                "message": "Profile retrieved successfully",
                "user": user.to_dict()
            }, 200
            
        except Exception as error:
            return {
                "message": "An error occurred while fetching profile",
                "error": str(error)
            }, 500

    @jwt_required()
    def put(self):
        """Update user profile"""
        try:
            current_user_id = get_jwt_identity()
            user_uuid = uuid.UUID(current_user_id)
            user = User.query.filter_by(id=user_uuid).first()
            
            if not user:
                return {"message": "User not found"}, 404
            
            # Handle profile image upload
            if 'profile_image' in request.files:
                file = request.files['profile_image']
                
                # Delete old image if exists
                if user.profile_image_id:
                    delete_image(user.profile_image_id)
                
                # Upload new image
                result = upload_image(file, 'profile_images')
                if not result['success']:
                    return {
                        "message": "Failed to upload image",
                        "error": result['error']
                    }, 400
                
                user.profile_image = result['url']
                user.profile_image_id = result['public_id']
            
            # Update other fields
            data = request.form.to_dict()
            
            if 'phonenumber' in data:
                user.phonenumber = data['phonenumber']
            
            db.session.commit()
            
            return {
                "message": "Profile updated successfully",
                "user": user.to_dict()
            }, 200
            
        except Exception as error:
            db.session.rollback()
            return {
                "message": "An error occurred while updating profile",
                "error": str(error)
            }, 500

class UserList(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """Get list of all users (admin only)"""
        try:
            users = User.query.all()
            users_data = [user.to_dict() for user in users]
            
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
api.add_resource(UserProfile, '/profile')
api.add_resource(UserList, '/users')