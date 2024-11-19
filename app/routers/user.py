from flask import Blueprint, request
from flask_restful import Resource, Api
from app.models import User
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps

user_bp = Blueprint('user', __name__)
api = Api(user_bp)

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)
        
        if not current_user or current_user.role != 'admin':
            return {'message': 'Admin privileges required'}, 403
            
        return f(*args, **kwargs)
    return decorated_function

class UserList(Resource):
    @jwt_required()
    def get(self):
        try:
            
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            # Query all users
            users = User.query.all()
            
            # Prepare response data based on role
            if current_user.role == 'admin':
                users_data = [{
                    "id": str(user.id),
                    "username": user.username,
                    "role": user.role,
                    "phonenumber": user.phonenumber
                } for user in users]
            else:
                # Regular users can only see limited info
                users_data = [{
                    "username": user.username,
                    "role": user.role
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

    @jwt_required()
    @admin_required
    def post(self):
        """Create new user (admin only)"""
        try:
            data = request.get_json()
            
            # Check for existing user
            if User.query.filter_by(username=data["username"]).first():
                return {"message": "Username already exists"}, 400
                
            # Create new user
            new_user = User(
                username=data["username"],
                phonenumber=data["phonenumber"],
                password=data["password"],
                role=data["role"]
            )
            
            db.session.add(new_user)
            db.session.commit()
            
            return {
                "message": "User created successfully",
                "user": {
                    "id": str(new_user.id),
                    "username": new_user.username,
                    "role": new_user.role,
                    "phonenumber": new_user.phonenumber
                }
            }, 201
            
        except Exception as error:
            db.session.rollback()
            return {
                "message": "An error occurred while creating user",
                "error": str(error)
            }, 500

class UserDetail(Resource):
    @jwt_required()
    def get(self, user_id):
        """Get user details by ID (requires authentication)"""
        try:
            # Get current user for role check
            current_user_id = get_jwt_identity()
            current_user = User.query.get(current_user_id)
            
            # Query requested user
            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found"}, 404
            
            # Prepare response data based on role
            if current_user.role == 'admin':
                user_data = {
                    "id": str(user.id),
                    "username": user.username,
                    "role": user.role,
                    "phonenumber": user.phonenumber
                }
            else:
                # Regular users can only see limited info
                if str(current_user.id) != user_id:
                    return {"message": "Access denied"}, 403
                user_data = {
                    "username": user.username,
                    "role": user.role
                }
            
            return {
                "message": "User retrieved successfully",
                "user": user_data
            }, 200
            
        except Exception as error:
            return {
                "message": "An error occurred while fetching user",
                "error": str(error)
            }, 500

    @jwt_required()
    @admin_required
    def put(self, user_id):
        """Update user details (admin only)"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found"}, 404
                
            data = request.get_json()
            
            # Update fields
            if 'username' in data:
                user.username = data['username']
            if 'phonenumber' in data:
                user.phonenumber = data['phonenumber']
            if 'role' in data:
                user.role = data['role']
            
            db.session.commit()
            
            return {
                "message": "User updated successfully",
                "user": {
                    "id": str(user.id),
                    "username": user.username,
                    "role": user.role,
                    "phonenumber": user.phonenumber
                }
            }, 200
            
        except Exception as error:
            db.session.rollback()
            return {
                "message": "An error occurred while updating user",
                "error": str(error)
            }, 500

    @jwt_required()
    @admin_required
    def delete(self, user_id):
        """Delete user (admin only)"""
        try:
            user = User.query.get(user_id)
            if not user:
                return {"message": "User not found"}, 404
                
            db.session.delete(user)
            db.session.commit()
            
            return {
                "message": "User deleted successfully"
            }, 200
            
        except Exception as error:
            db.session.rollback()
            return {
                "message": "An error occurred while deleting user",
                "error": str(error)
            }, 500

# Register routes
api.add_resource(UserList, '/users')
api.add_resource(UserDetail, '/users/<string:user_id>') 