from flask import Blueprint, request
from flask_restful import Resource, Api
from app.models import Service
from app.extensions import db
from flask_jwt_extended import jwt_required
from app.middleware.auth_middleware import admin_required
import uuid

service_bp = Blueprint('service', __name__)
api = Api(service_bp)

class ServiceList(Resource):
    @jwt_required()
    def get(self):
        """Get all services (public access)"""
        try:
            services = Service.query.all()
            services_data = [{
                "id": str(service.id),
                "service_name": service.service_name,
                "description": service.description,
                "price": service.price,
                "duration": service.duration,
                "vehicle_type": service.vehicle_type
            } for service in services]
            
            return {
                "message": "Services retrieved successfully",
                "services": services_data,
                "total": len(services_data)
            }, 200
            
        except Exception as error:
            return {
                "message": "An error occurred while fetching services",
                "error": str(error)
            }, 500

    @jwt_required()
    @admin_required
    def post(self):
        """Create new service (admin only)"""
        try:
            data = request.get_json()
            
            new_service = Service(
                service_name=data["service_name"],
                description=data["description"],
                price=data["price"],
                duration=data["duration"],
                vehicle_type=data["vehicle_type"]
            )
            
            db.session.add(new_service)
            db.session.commit()
            
            return {
                "message": "Service created successfully",
                "service": {
                    "id": str(new_service.id),
                    "service_name": new_service.service_name,
                    "description": new_service.description,
                    "price": new_service.price,
                    "duration": new_service.duration,
                    "vehicle_type": new_service.vehicle_type
                }
            }, 201
            
        except Exception as error:
            db.session.rollback()
            return {
                "message": "An error occurred while creating service",
                "error": str(error)
            }, 500

class ServiceDetail(Resource):
    def get(self, service_id):
        """Get service details by ID (public access)"""
        try:
            service_uuid = uuid.UUID(service_id)
            service = Service.query.filter_by(id=service_uuid).first()
            
            if not service:
                return {"message": "Service not found"}, 404
            
            return {
                "message": "Service retrieved successfully",
                "service": {
                    "id": str(service.id),
                    "service_name": service.service_name,
                    "description": service.description,
                    "price": service.price,
                    "duration": service.duration,
                    "vehicle_type": service.vehicle_type
                }
            }, 200
            
        except ValueError:
            return {"message": "Invalid service ID format"}, 400
        except Exception as error:
            return {
                "message": "An error occurred while fetching service",
                "error": str(error)
            }, 500

    @jwt_required()
    @admin_required
    def put(self, service_id):
        """Update service details (admin only)"""
        try:
            service_uuid = uuid.UUID(service_id)
            service = Service.query.filter_by(id=service_uuid).first()
            
            if not service:
                return {"message": "Service not found"}, 404
            
            data = request.get_json()
            
            # Update fields if provided
            if "service_name" in data:
                service.service_name = data["service_name"]
            if "description" in data:
                service.description = data["description"]
            if "price" in data:
                service.price = data["price"]
            if "duration" in data:
                service.duration = data["duration"]
            if "vehicle_type" in data:
                service.vehicle_type = data["vehicle_type"]
            
            db.session.commit()
            
            return {
                "message": "Service updated successfully",
                "service": {
                    "id": str(service.id),
                    "service_name": service.service_name,
                    "description": service.description,
                    "price": service.price,
                    "duration": service.duration,
                    "vehicle_type": service.vehicle_type
                }
            }, 200
            
        except ValueError:
            return {"message": "Invalid service ID format"}, 400
        except Exception as error:
            db.session.rollback()
            return {
                "message": "An error occurred while updating service",
                "error": str(error)
            }, 500

    @jwt_required()
    @admin_required
    def delete(self, service_id):
        """Delete service (admin only)"""
        try:
            service_uuid = uuid.UUID(service_id)
            service = Service.query.filter_by(id=service_uuid).first()
            
            if not service:
                return {"message": "Service not found"}, 404
            
            db.session.delete(service)
            db.session.commit()
            
            return {
                "message": "Service deleted successfully"
            }, 200
            
        except ValueError:
            return {"message": "Invalid service ID format"}, 400
        except Exception as error:
            db.session.rollback()
            return {
                "message": "An error occurred while deleting service",
                "error": str(error)
            }, 500

# Register routes
api.add_resource(ServiceList, '/services')
api.add_resource(ServiceDetail, '/services/<string:service_id>') 