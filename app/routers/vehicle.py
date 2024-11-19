from flask import Blueprint, request
from flask_restful import Resource, Api
from app.models import Vehicle, User
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middleware.auth_middleware import user_admin_required
import uuid

vehicle_bp = Blueprint('vehicle', __name__)
api = Api(vehicle_bp)

class VehicleList(Resource):
    @jwt_required()
    def get(self):
        """Get all vehicles for the current user"""
        try:
            current_user_id = get_jwt_identity()
            user_uuid = uuid.UUID(current_user_id)
            
            # Get vehicles for current user
            vehicles = Vehicle.query.filter_by(user_id=user_uuid).all()
            
            vehicles_data = [{
                "id": str(vehicle.id),
                "vehicle_name": vehicle.vehicle_name,
                "vehicle_model": vehicle.vehicle_model,
                "numberplate": vehicle.numberplate,
                "vehicle_type": vehicle.vehicle_type,
                "vehicle_image": vehicle.vehicle_image
            } for vehicle in vehicles]
            
            return {
                "message": "Vehicles retrieved successfully",
                "vehicles": vehicles_data,
                "total": len(vehicles_data)
            }, 200
            
        except Exception as error:
            return {
                "message": "An error occurred while fetching vehicles",
                "error": str(error)
            }, 500

    @jwt_required()
    def post(self):
        """Create new vehicle (authenticated users only)"""
        try:
            current_user_id = get_jwt_identity()
            user_uuid = uuid.UUID(current_user_id)
            
            data = request.get_json()
            
            # Check if numberplate already exists
            if Vehicle.query.filter_by(numberplate=data["numberplate"]).first():
                return {"message": "Vehicle with this numberplate already exists"}, 400
            
            new_vehicle = Vehicle(
                vehicle_name=data["vehicle_name"],
                vehicle_model=data["vehicle_model"],
                numberplate=data["numberplate"],
                vehicle_type=data["vehicle_type"],
                vehicle_image=data.get("vehicle_image"),  # Optional
                user_id=user_uuid
            )
            
            db.session.add(new_vehicle)
            db.session.commit()
            
            return {
                "message": "Vehicle created successfully",
                "vehicle": {
                    "id": str(new_vehicle.id),
                    "vehicle_name": new_vehicle.vehicle_name,
                    "vehicle_model": new_vehicle.vehicle_model,
                    "numberplate": new_vehicle.numberplate,
                    "vehicle_type": new_vehicle.vehicle_type,
                    "vehicle_image": new_vehicle.vehicle_image
                }
            }, 201
            
        except Exception as error:
            db.session.rollback()
            return {
                "message": "An error occurred while creating vehicle",
                "error": str(error)
            }, 500

class VehicleDetail(Resource):
    @jwt_required()
    def get(self, vehicle_id):
        """Get vehicle details (owner or admin only)"""
        try:
            current_user_id = get_jwt_identity()
            user_uuid = uuid.UUID(current_user_id)
            
            vehicle = Vehicle.query.get(vehicle_id)
            if not vehicle:
                return {"message": "Vehicle not found"}, 404
            
            # Check if user is owner
            if str(vehicle.user_id) != current_user_id:
                # Check if user is admin
                user = User.query.get(user_uuid)
                if user.role != 'admin':
                    return {"message": "Access denied"}, 403
            
            return {
                "message": "Vehicle retrieved successfully",
                "vehicle": {
                    "id": str(vehicle.id),
                    "vehicle_name": vehicle.vehicle_name,
                    "vehicle_model": vehicle.vehicle_model,
                    "numberplate": vehicle.numberplate,
                    "vehicle_type": vehicle.vehicle_type,
                    "vehicle_image": vehicle.vehicle_image
                }
            }, 200
            
        except Exception as error:
            return {
                "message": "An error occurred while fetching vehicle",
                "error": str(error)
            }, 500

    @jwt_required()
    def put(self, vehicle_id):
        """Update vehicle details (owner only)"""
        try:
            current_user_id = get_jwt_identity()
            
            vehicle = Vehicle.query.get(vehicle_id)
            if not vehicle:
                return {"message": "Vehicle not found"}, 404
            
            # Check if user is owner
            if str(vehicle.user_id) != current_user_id:
                return {"message": "Access denied"}, 403
            
            data = request.get_json()
            
            # Update fields if provided
            if "vehicle_name" in data:
                vehicle.vehicle_name = data["vehicle_name"]
            if "vehicle_model" in data:
                vehicle.vehicle_model = data["vehicle_model"]
            if "numberplate" in data:
                # Check if new numberplate already exists
                existing = Vehicle.query.filter_by(numberplate=data["numberplate"]).first()
                if existing and existing.id != vehicle.id:
                    return {"message": "Vehicle with this numberplate already exists"}, 400
                vehicle.numberplate = data["numberplate"]
            if "vehicle_type" in data:
                vehicle.vehicle_type = data["vehicle_type"]
            if "vehicle_image" in data:
                vehicle.vehicle_image = data["vehicle_image"]
            
            db.session.commit()
            
            return {
                "message": "Vehicle updated successfully",
                "vehicle": {
                    "id": str(vehicle.id),
                    "vehicle_name": vehicle.vehicle_name,
                    "vehicle_model": vehicle.vehicle_model,
                    "numberplate": vehicle.numberplate,
                    "vehicle_type": vehicle.vehicle_type,
                    "vehicle_image": vehicle.vehicle_image
                }
            }, 200
            
        except Exception as error:
            db.session.rollback()
            return {
                "message": "An error occurred while updating vehicle",
                "error": str(error)
            }, 500

    @jwt_required()
    def delete(self, vehicle_id):
        """Delete vehicle (owner only)"""
        try:
            current_user_id = get_jwt_identity()
            
            vehicle = Vehicle.query.get(vehicle_id)
            if not vehicle:
                return {"message": "Vehicle not found"}, 404
            
            # Check if user is owner
            if str(vehicle.user_id) != current_user_id:
                return {"message": "Access denied"}, 403
            
            db.session.delete(vehicle)
            db.session.commit()
            
            return {
                "message": "Vehicle deleted successfully"
            }, 200
            
        except Exception as error:
            db.session.rollback()
            return {
                "message": "An error occurred while deleting vehicle",
                "error": str(error)
            }, 500

class AllVehicles(Resource):
    @jwt_required()
    @user_admin_required
    def get(self):
        """Get all vehicles (admin only)"""
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

# Register routes
api.add_resource(VehicleList, '/vehicles')  # User's vehicles
api.add_resource(VehicleDetail, '/vehicles/<string:vehicle_id>')  # Single vehicle operations
api.add_resource(AllVehicles, '/all-vehicles')  # Admin view of all vehicles 