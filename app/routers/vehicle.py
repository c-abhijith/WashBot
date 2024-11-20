from flask import Blueprint, request
from flask_restful import Resource, Api
from app.models import Vehicle, User
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middleware.auth_middleware import user_admin_required
import uuid
from app.response import success_response,server_response
from app.helper.body_validator import vechile_validation

vehicle_bp = Blueprint('vehicle', __name__)
api = Api(vehicle_bp)

class VehicleList(Resource):
    @jwt_required()
    def get(self):
        try:
            vehicles = Vehicle.query.all()
            vehicles_data = [success_response.vechile_list(vehicle) for vehicle in vehicles]
            return success_response.vechile_response(vehicles_data), 200
            
        except Exception as error:
            return server_response.data_error(error), 500

    @jwt_required()
    def post(self):
        try:
            user_id = get_jwt_identity()
            data = request.get_json()
            vechile=vechile_validation(data)
            if vechile:
                return vechile

            new_vehicle = Vehicle(
                vehicle_name=data["vehicle_name"],
                vehicle_model=data["vehicle_model"],
                numberplate=data["numberplate"],
                vehicle_type=data["vehicle_type"],
                user_id=user_id
            )
            
            db.session.add(new_vehicle)
            db.session.commit()
            return success_response.vechile_create(new_vehicle), 201
            
        except Exception as error:
            db.session.rollback()
            return server_response.data_error(error), 500

class VehicleDetail(Resource):
    @jwt_required()
    def get(self, vehicle_id):
       
        try:
            vehicle = Vehicle.query.get(vehicle_id)
            if not vehicle:
                return {"message": "Vehicle not found"}, 404
            
            return success_response.vechile_details(vehicle), 200
            
        except Exception as error:
            return server_response.data_error(error), 500

    @jwt_required()
    def put(self, vehicle_id):
        try:
            user_id = get_jwt_identity()
            
            vehicle = Vehicle.query.get(vehicle_id)
            if not vehicle:
                return {"message": "Vehicle not found"}, 404
            
            data = request.get_json()
            
            if "vehicle_name" in data:
                vehicle.vehicle_name = data["vehicle_name"]
            if "vehicle_model" in data:
                vehicle.vehicle_model = data["vehicle_model"]
            if "numberplate" in data:
                existing = Vehicle.query.filter_by(numberplate=data["numberplate"]).first()
                if existing and existing.id != vehicle.id:
                    return {"message": "Vehicle with this numberplate already exists"}, 400
                vehicle.numberplate = data["numberplate"]
            if "vehicle_type" in data:
                vehicle.vehicle_type = data["vehicle_type"]
           
            
            db.session.commit()
            
            return success_response.vechile_details(vehicle), 200
            
        except Exception as error:
            db.session.rollback()
            return server_response.data_error(error), 500

    @jwt_required()
    def delete(self, vehicle_id):
        try:
            vehicle = Vehicle.query.get(vehicle_id)
            if not vehicle:
                return {"message": "Vehicle not found"}, 404

            db.session.delete(vehicle)
            db.session.commit()
            
            return {
                "message": "Vehicle deleted successfully"
            }, 200
            
        except Exception as error:
            db.session.rollback()
            return server_response.data_error(error), 500

class AllVehicles(Resource):
    @jwt_required()
    @user_admin_required
    def get(self):
        try:
            vehicles = Vehicle.query.all()
            vehicles_data = [{
                "id": str(vehicle.id),
                "vehicle_name": vehicle.vehicle_name,
                "vehicle_model": vehicle.vehicle_model,
                "numberplate": vehicle.numberplate,
                "vehicle_type": vehicle.vehicle_type,
                "vehicle_image": vehicle.vehicle_image,
                "user_id": str(vehicle.user_id)
            } for vehicle in vehicles]
            
            return {
                "message": "All vehicles retrieved successfully",
                "vehicles": vehicles_data,
                "total": len(vehicles_data)
            }, 200
            
        except Exception as error:
            return {
                "message": "An error occurred while fetching vehicles",
                "error": str(error)
            }, 500


api.add_resource(VehicleList, '/vehicles')  
api.add_resource(VehicleDetail, '/vehicles/<string:vehicle_id>') 
api.add_resource(AllVehicles, '/all-vehicles')  