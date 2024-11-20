from flask import Blueprint, request, current_app
from flask_restful import Resource, Api
from app.models import User
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middleware.auth_middleware import admin_required
from app.helper.cloudinary_helper import upload_image, delete_image
import uuid
from app.response import success_response,server_response

user_bp = Blueprint('user', __name__)
api = Api(user_bp)

class UserProfile(Resource):
    @jwt_required()
    def get(self):
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(id=user_id).first()
            
            if not user:
                return {"message": "User not found"}, 404
            print(user)
            return success_response.userdata(user), 200
        except Exception as error:
            return server_response.data_error(error), 500

    @jwt_required()
    def put(self):
        try:
            user_id = get_jwt_identity()
            user = User.query.filter_by(id=user_id).first()
            
            if not user:
                return {"message": "User not found"}, 404
        
        
            data = request.get_json()
            if not data:
                return {"message": "No data provided"}, 400
            
            for field in ['username', 'phonenumber']:
                if field in data:
                    setattr(user, field, data[field])
                    
            db.session.commit()
            
            return success_response.userdata(user), 200
            
        except Exception as error:
            db.session.rollback()
            return server_response.data_error(error), 500

class UserList(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        try:
            users = User.query.all()
            users_data = [success_response.user_to_dict(user) for user in users]
            
            return success_response.user_all(users_data), 200
            
        except Exception as error:
            return server_response.data_error(error), 500


api.add_resource(UserProfile, '/profile')
api.add_resource(UserList, '/users')