from flask import Blueprint, request, current_app
from flask_restful import Resource, Api
from app.models import Booking, Service, Vehicle, Payment, User
from app.extensions import db
from flask_jwt_extended import jwt_required, get_jwt_identity
from app.middleware.auth_middleware import admin_required, user_admin_required, staff_admin_required
from app.helper.payment_helper import PaymentGateway
import uuid
from datetime import datetime

booking_bp = Blueprint('booking', __name__)
api = Api(booking_bp)

class BookingList(Resource):
    @jwt_required()
    def get(self):
        """Get all bookings for current user"""
        try:
            current_user_id = get_jwt_identity()
            user_uuid = uuid.UUID(current_user_id)
            
            bookings = Booking.query.filter_by(user_id=user_uuid).all()
            
            bookings_data = [{
                "id": str(booking.id),
                "service": {
                    "id": str(booking.service.id),
                    "name": booking.service.service_name,
                    "price": booking.service.price
                },
                "vehicle": {
                    "id": str(booking.vehicle.id),
                    "name": booking.vehicle.vehicle_name,
                    "numberplate": booking.vehicle.numberplate
                },
                "date": booking.date.strftime('%Y-%m-%d'),
                "time_from": booking.time_from.strftime('%H:%M'),
                "time_to": booking.time_to.strftime('%H:%M'),
                "duration": booking.duration,
                "total_amount": booking.total_amount,
                "status": booking.status,
                "payment_status": booking.payment.payment_status if booking.payment else "no_payment",
                "created_at": booking.created_at.strftime('%Y-%m-%d %H:%M:%S')
            } for booking in bookings]
            
            return {
                "message": "Bookings retrieved successfully",
                "bookings": bookings_data,
                "total": len(bookings_data)
            }, 200
            
        except Exception as error:
            return {
                "message": "An error occurred while fetching bookings",
                "error": str(error)
            }, 500

    @jwt_required()
    def post(self):
        """Create new booking"""
        try:
            current_user_id = get_jwt_identity()
            user_uuid = uuid.UUID(current_user_id)
            
            data = request.get_json()
            
            # Validate service and vehicle
            service = Service.query.get(data['service_id'])
            vehicle = Vehicle.query.get(data['vehicle_id'])
            
            if not service or not vehicle:
                return {"message": "Invalid service or vehicle ID"}, 400
            
            # Verify vehicle belongs to user
            if str(vehicle.user_id) != current_user_id:
                return {"message": "Vehicle does not belong to user"}, 403
            
            # Create booking
            booking = Booking(
                user_id=user_uuid,
                service_id=uuid.UUID(data['service_id']),
                vehicle_id=uuid.UUID(data['vehicle_id']),
                date=datetime.strptime(data['date'], '%Y-%m-%d').date(),
                time_from=datetime.strptime(data['time_from'], '%H:%M').time(),
                time_to=datetime.strptime(data['time_to'], '%H:%M').time(),
                duration=service.duration,
                total_amount=service.price,
                status='pending'
            )
            
            db.session.add(booking)
            db.session.commit()
            
            # Initialize payment based on method
            payment_method = data.get('payment_method', 'stripe')
            payment = Payment(
                booking_id=booking.id,
                amount=service.price,
                payment_method=payment_method,
                payment_status='pending'
            )
            
            db.session.add(payment)
            db.session.commit()
            
            # Create payment intent/order
            if payment_method == 'stripe':
                payment_data = PaymentGateway.create_stripe_payment(service.price)
            elif payment_method == 'razorpay':
                payment_data = PaymentGateway.create_razorpay_payment(service.price)
            elif payment_method == 'paypal':
                payment_data = PaymentGateway.create_paypal_payment(service.price)
            
            if not payment_data['success']:
                return {"message": "Payment initialization failed", "error": payment_data.get('error')}, 400
            
            payment.payment_response = payment_data
            db.session.commit()
            
            return {
                "message": "Booking created successfully",
                "booking": {
                    "id": str(booking.id),
                    "service": {
                        "id": str(service.id),
                        "name": service.service_name,
                        "price": service.price
                    },
                    "payment_data": payment_data,
                    "total_amount": booking.total_amount
                }
            }, 201
            
        except Exception as error:
            db.session.rollback()
            return {
                "message": "An error occurred while creating booking",
                "error": str(error)
            }, 500

class BookingDetail(Resource):
    @jwt_required()
    def get(self, booking_id):
        """Get booking details"""
        try:
            current_user_id = get_jwt_identity()
            booking = Booking.query.get(booking_id)
            
            if not booking:
                return {"message": "Booking not found"}, 404
            
            # Check if user owns booking or is admin
            if str(booking.user_id) != current_user_id:
                user = User.query.get(current_user_id)
                if user.role != 'admin':
                    return {"message": "Access denied"}, 403
            
            return {
                "message": "Booking retrieved successfully",
                "booking": {
                    "id": str(booking.id),
                    "service": {
                        "id": str(booking.service.id),
                        "name": booking.service.service_name,
                        "price": booking.service.price
                    },
                    "vehicle": {
                        "id": str(booking.vehicle.id),
                        "name": booking.vehicle.vehicle_name,
                        "numberplate": booking.vehicle.numberplate
                    },
                    "date": booking.date.strftime('%Y-%m-%d'),
                    "time_from": booking.time_from.strftime('%H:%M'),
                    "time_to": booking.time_to.strftime('%H:%M'),
                    "duration": booking.duration,
                    "total_amount": booking.total_amount,
                    "status": booking.status,
                    "payment": {
                        "status": booking.payment.payment_status,
                        "method": booking.payment.payment_method,
                        "transaction_id": booking.payment.transaction_id
                    } if booking.payment else None
                }
            }, 200
            
        except Exception as error:
            return {
                "message": "An error occurred while fetching booking",
                "error": str(error)
            }, 500

    @jwt_required()
    @staff_admin_required
    def put(self, booking_id):
        """Update booking status (staff/admin only)"""
        try:
            data = request.get_json()
            if 'status' not in data:
                return {"message": "Status is required"}, 400

            booking = Booking.query.get(booking_id)
            if not booking:
                return {"message": "Booking not found"}, 404

            # Validate status transition
            valid_statuses = ['confirmed', 'startservice', 'complete', 'cancelled']
            if data['status'] not in valid_statuses:
                return {
                    "message": "Invalid status",
                    "valid_statuses": valid_statuses
                }, 400

            # Get current user role
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            # Status transition rules
            if data['status'] == 'cancelled':
                if user.role != 'admin':
                    return {"message": "Only admin can cancel bookings"}, 403
            
            # Update status
            old_status = booking.status
            booking.status = data['status']
            
            # If status is complete, update payment status
            if data['status'] == 'complete' and booking.payment:
                booking.payment.payment_status = 'completed'

            db.session.commit()

            return {
                "message": "Booking status updated successfully",
                "booking": {
                    "id": str(booking.id),
                    "old_status": old_status,
                    "new_status": booking.status,
                    "service": {
                        "id": str(booking.service.id),
                        "name": booking.service.service_name
                    },
                    "vehicle": {
                        "id": str(booking.vehicle.id),
                        "numberplate": booking.vehicle.numberplate
                    },
                    "customer": {
                        "id": str(booking.user.id),
                        "username": booking.user.username
                    },
                    "updated_by": {
                        "id": str(user.id),
                        "username": user.username,
                        "role": user.role
                    }
                }
            }, 200

        except Exception as error:
            db.session.rollback()
            return {
                "message": "An error occurred while updating booking status",
                "error": str(error)
            }, 500

    @jwt_required()
    @staff_admin_required
    def patch(self, booking_id):
        """Update booking status (staff/admin only)"""
        try:
            data = request.get_json()
            if 'status' not in data:
                return {"message": "Status is required"}, 400

            booking = Booking.query.get(booking_id)
            if not booking:
                return {"message": "Booking not found"}, 404

            # Validate status transition
            valid_statuses = ['confirmed', 'startservice', 'complete', 'cancelled']
            if data['status'] not in valid_statuses:
                return {
                    "message": "Invalid status",
                    "valid_statuses": valid_statuses
                }, 400

            # Get current user role
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            # Status transition rules
            if data['status'] == 'cancelled':
                if user.role != 'admin':
                    return {"message": "Only admin can cancel bookings"}, 403
            
            # Update status
            old_status = booking.status
            booking.status = data['status']
            
            # If status is complete, update payment status
            if data['status'] == 'complete' and booking.payment:
                booking.payment.payment_status = 'completed'

            db.session.commit()

            return {
                "message": "Booking status updated successfully",
                "booking": {
                    "id": str(booking.id),
                    "old_status": old_status,
                    "new_status": booking.status,
                    "service": {
                        "id": str(booking.service.id),
                        "name": booking.service.service_name
                    },
                    "vehicle": {
                        "id": str(booking.vehicle.id),
                        "numberplate": booking.vehicle.numberplate
                    },
                    "customer": {
                        "id": str(booking.user.id),
                        "username": booking.user.username
                    },
                    "updated_by": {
                        "id": str(user.id),
                        "username": user.username,
                        "role": user.role
                    }
                }
            }, 200

        except Exception as error:
            db.session.rollback()
            return {
                "message": "An error occurred while updating booking status",
                "error": str(error)
            }, 500

    @jwt_required()
    def delete(self, booking_id):
        """Cancel booking"""
        try:
            current_user_id = get_jwt_identity()
            booking = Booking.query.get(booking_id)
            
            if not booking:
                return {"message": "Booking not found"}, 404
            
            # Check if user owns booking
            if str(booking.user_id) != current_user_id:
                return {"message": "Access denied"}, 403
            
            # Only allow cancellation of pending bookings
            if booking.status != 'pending':
                return {"message": "Cannot cancel non-pending booking"}, 400
            
            booking.status = 'cancelled'
            db.session.commit()
            
            return {
                "message": "Booking cancelled successfully"
            }, 200
            
        except Exception as error:
            db.session.rollback()
            return {
                "message": "An error occurred while cancelling booking",
                "error": str(error)
            }, 500

class AllBookings(Resource):
    @jwt_required()
    @admin_required
    def get(self):
        """Get all bookings (admin only)"""
        try:
            bookings = Booking.query.all()
            
            bookings_data = [{
                "id": str(booking.id),
                "user": {
                    "id": str(booking.user.id),
                    "username": booking.user.username
                },
                "service": {
                    "id": str(booking.service.id),
                    "name": booking.service.service_name
                },
                "vehicle": {
                    "id": str(booking.vehicle.id),
                    "numberplate": booking.vehicle.numberplate
                },
                "date": booking.date.strftime('%Y-%m-%d'),
                "status": booking.status,
                "payment_status": booking.payment.payment_status if booking.payment else "no_payment"
            } for booking in bookings]
            
            return {
                "message": "All bookings retrieved successfully",
                "bookings": bookings_data,
                "total": len(bookings_data)
            }, 200
            
        except Exception as error:
            return {
                "message": "An error occurred while fetching bookings",
                "error": str(error)
            }, 500

class BookingStatusUpdate(Resource):
    @jwt_required()
    @staff_admin_required
    def post(self, booking_id, status):
        """Quick status update endpoint (staff/admin only)"""
        try:
            booking = Booking.query.get(booking_id)
            if not booking:
                return {"message": "Booking not found"}, 404

            # Validate status
            valid_statuses = ['confirmed', 'startservice', 'complete', 'cancelled']
            if status not in valid_statuses:
                return {
                    "message": "Invalid status",
                    "valid_statuses": valid_statuses
                }, 400

            # Get current user role
            current_user_id = get_jwt_identity()
            user = User.query.get(current_user_id)

            # Status transition rules
            if status == 'cancelled' and user.role != 'admin':
                return {"message": "Only admin can cancel bookings"}, 403

            # Update status
            old_status = booking.status
            booking.status = status

            # If status is complete, update payment status
            if status == 'complete' and booking.payment:
                booking.payment.payment_status = 'completed'

            db.session.commit()

            return {
                "message": "Booking status updated successfully",
                "booking": {
                    "id": str(booking.id),
                    "old_status": old_status,
                    "new_status": status,
                    "updated_by": {
                        "username": user.username,
                        "role": user.role
                    }
                }
            }, 200

        except Exception as error:
            db.session.rollback()
            return {
                "message": "An error occurred while updating booking status",
                "error": str(error)
            }, 500

# Register routes
api.add_resource(BookingList, '/bookings')
api.add_resource(BookingDetail, '/bookings/<string:booking_id>')
api.add_resource(BookingStatusUpdate, '/bookings/<string:booking_id>/status/<string:status>')
api.add_resource(AllBookings, '/all-bookings') 