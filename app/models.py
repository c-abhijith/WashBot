from app.extensions import db
from datetime import datetime
import json
import uuid

def get_uuid():
    return str(uuid.uuid4())

class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.String(36), primary_key=True, default=get_uuid)
    profile_image = db.Column(db.String(255), nullable=True)
    profile_image_id = db.Column(db.String(255), nullable=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    phonenumber = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(10), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Vehicle(db.Model):
    __tablename__ = 'vehicle'
    id = db.Column(db.String(36), primary_key=True, default=get_uuid)
    vehicle_image = db.Column(db.String(255), nullable=True)
    vehicle_name = db.Column(db.String(100), nullable=False)
    vehicle_model = db.Column(db.String(100), nullable=False)
    numberplate = db.Column(db.String(50), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(10), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref='vehicles')

class Service(db.Model):
    __tablename__ = 'service'
    id = db.Column(db.String(36), primary_key=True, default=get_uuid)
    service_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    vehicle_type = db.Column(db.String(10), nullable=False)

class Booking(db.Model):
    __tablename__ = 'booking'
    id = db.Column(db.String(36), primary_key=True, default=get_uuid)
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)
    service_id = db.Column(db.String(36), db.ForeignKey('service.id'), nullable=False)
    vehicle_id = db.Column(db.String(36), db.ForeignKey('vehicle.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_from = db.Column(db.Time, nullable=False)
    time_to = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    total_amount = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(20), nullable=False, default='pending')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='bookings')
    service = db.relationship('Service', backref='bookings')
    vehicle = db.relationship('Vehicle', backref='bookings')

class Payment(db.Model):
    __tablename__ = 'payment'
    id = db.Column(db.String(36), primary_key=True, default=get_uuid)
    booking_id = db.Column(db.String(36), db.ForeignKey('booking.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    payment_method = db.Column(db.String(20), nullable=False)
    payment_status = db.Column(db.String(20), nullable=False, default='pending')
    transaction_id = db.Column(db.String(255), unique=True, nullable=True)
    payment_response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    booking = db.relationship('Booking', backref=db.backref('payment', uselist=False))
