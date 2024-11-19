import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db


class User(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    profile_image = db.Column(db.String(255), nullable=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    phonenumber = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.Enum('user', 'admin','staff', name='user_roles'), nullable=False)

class Vehicle(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    vehicle_image = db.Column(db.String(255), nullable=True)
    vehicle_name = db.Column(db.String(100), nullable=False)
    vehicle_model = db.Column(db.String(100), nullable=False)
    numberplate = db.Column(db.String(50), unique=True, nullable=False)
    vehicle_type = db.Column(db.Enum('car', 'bike', name='vehicle_types'), nullable=False)
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.id'), nullable=False)

class Service(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False) 
    vehicle_type = db.Column(db.Enum('car', 'bike', name='service_vehicle_types'), nullable=False)

class Booking(db.Model):
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    service_id = db.Column(UUID(as_uuid=True), db.ForeignKey('service.id'), nullable=False)
    vehicle_id = db.Column(UUID(as_uuid=True), db.ForeignKey('vehicle.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_from = db.Column(db.Time, nullable=False)
    time_to = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    status = db.Column(
        db.Enum('booked','pending', 'startservice', 'complete', name='booking_status'), 
        nullable=False
    )
