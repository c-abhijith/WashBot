import uuid
from sqlalchemy.dialects.postgresql import UUID
from app.extensions import db
from datetime import datetime


class User(db.Model):
    id = db.Column(
        db.String(36),  # Using String for SQLite compatibility
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    profile_image = db.Column(db.String(255), nullable=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    phonenumber = db.Column(db.String(15), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(
        db.Enum('user', 'admin', 'staff', name='user_roles'),
        nullable=False
    )


class Vehicle(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    vehicle_image = db.Column(db.String(255), nullable=True)
    vehicle_name = db.Column(db.String(100), nullable=False)
    vehicle_model = db.Column(db.String(100), nullable=False)
    numberplate = db.Column(db.String(50), unique=True, nullable=False)
    vehicle_type = db.Column(
        db.Enum('car', 'bike', name='vehicle_types'),
        nullable=False
    )
    user_id = db.Column(db.String(36), db.ForeignKey('user.id'), nullable=False)


class Service(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    service_name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    price = db.Column(db.Float, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    vehicle_type = db.Column(
        db.Enum('car', 'bike', name='service_vehicle_types'),
        nullable=False
    )


class Booking(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    service_id = db.Column(db.String(36), db.ForeignKey('service.id'), nullable=False)
    vehicle_id = db.Column(db.String(36), db.ForeignKey('vehicle.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    time_from = db.Column(db.Time, nullable=False)
    time_to = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Integer, nullable=False)
    status = db.Column(
        db.Enum(
            'pending', 'confirmed', 'startservice', 'complete', 'cancelled',
            name='booking_status'
        ),
        nullable=False,
        default='pending'
    )
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship('User', backref='bookings')
    service = db.relationship('Service', backref='bookings')
    vehicle = db.relationship('Vehicle', backref='bookings')


class Payment(db.Model):
    id = db.Column(
        db.String(36),
        primary_key=True,
        default=lambda: str(uuid.uuid4())
    )
    booking_id = db.Column(db.String(36), db.ForeignKey('booking.id'), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    currency = db.Column(db.String(3), nullable=False, default='USD')
    payment_method = db.Column(
        db.Enum('stripe', 'paypal', 'razorpay', name='payment_methods'),
        nullable=False
    )
    payment_status = db.Column(
        db.Enum('pending', 'completed', 'failed', 'refunded', name='payment_status'),
        nullable=False,
        default='pending'
    )
    transaction_id = db.Column(db.String(255), unique=True, nullable=True)
    payment_response = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationship
    booking = db.relationship('Booking', backref=db.backref('payment', uselist=False))
