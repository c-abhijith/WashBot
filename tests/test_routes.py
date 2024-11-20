import unittest
import json
from app import create_app
from app.extensions import db
from app.models import User, Service, Vehicle, Booking, Payment
from app.helper.auth_helper import password_hash
import uuid
from datetime import datetime, date, time

class TestRoutes(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        cls.client = cls.app.test_client()
        
        # Create application context
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # Create tables
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        # Create test users
        self.admin = User(
            username=f"admin_{uuid.uuid4().hex[:8]}",
            password=password_hash("admin123"),
            phonenumber="1234567890",
            role="admin"
        )
        
        self.staff = User(
            username=f"staff_{uuid.uuid4().hex[:8]}",
            password=password_hash("staff123"),
            phonenumber="0987654321",
            role="staff"
        )
        
        self.user = User(
            username=f"user_{uuid.uuid4().hex[:8]}",
            password=password_hash("user123"),
            phonenumber="1122334455",
            role="user"
        )
        
        db.session.add_all([self.admin, self.staff, self.user])
        db.session.commit()

    def tearDown(self):
        db.session.query(Payment).delete()
        db.session.query(Booking).delete()
        db.session.query(Vehicle).delete()
        db.session.query(Service).delete()
        db.session.query(User).delete()
        db.session.commit()

    def get_token(self, username, password):
        """Helper method to get auth token"""
        response = self.client.post('/login',
            json={
                "username": username,
                "password": password
            }
        )
        return json.loads(response.data)['accessToken']

    # Auth Tests
    def test_signup(self):
        """Test user registration"""
        data = {
            "username": f"test_user_{uuid.uuid4().hex[:8]}",
            "password": "test123",
            "phonenumber": "9876543210",
            "role": "user"
        }
        response = self.client.post('/signup', json=data)
        self.assertEqual(response.status_code, 201)
        self.assertIn('User created', json.loads(response.data)['message'])

    def test_login(self):
        """Test user login"""
        response = self.client.post('/login',
            json={
                "username": self.user.username,
                "password": "user123"
            }
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('accessToken', data)
        self.assertIn('refreshToken', data)

    # User Tests
    def test_get_profile(self):
        """Test getting user profile"""
        token = self.get_token(self.user.username, "user123")
        response = self.client.get('/user',
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertEqual(data['user']['username'], self.user.username)

    def test_get_users_admin(self):
        """Test getting all users (admin only)"""
        token = self.get_token(self.admin.username, "admin123")
        response = self.client.get('/user_list',
            headers={"Authorization": f"Bearer {token}"}
        )
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('users', data)

    # Service Tests
    def test_create_service(self):
        """Test creating service (admin only)"""
        token = self.get_token(self.admin.username, "admin123")
        service_data = {
            "service_name": "Test Service",
            "description": "Test Description",
            "price": 99.99,
            "duration": 60,
            "vehicle_type": "car"
        }
        response = self.client.post('/services',
            headers={"Authorization": f"Bearer {token}"},
            json=service_data
        )
        self.assertEqual(response.status_code, 201)

    # Vehicle Tests
    def test_create_vehicle(self):
        """Test creating vehicle"""
        token = self.get_token(self.user.username, "user123")
        vehicle_data = {
            "vehicle_name": "Test Car",
            "vehicle_model": "Test Model",
            "numberplate": f"TEST{uuid.uuid4().hex[:4]}",
            "vehicle_type": "car"
        }
        response = self.client.post('/vehicles',
            headers={"Authorization": f"Bearer {token}"},
            json=vehicle_data
        )
        self.assertEqual(response.status_code, 201)

    # Booking Tests
    def test_create_booking(self):
        """Test creating booking"""
        # First create a service
        token = self.get_token(self.admin.username, "admin123")
        service_data = {
            "service_name": "Test Service",
            "description": "Test Description",
            "price": 99.99,
            "duration": 60,
            "vehicle_type": "car"
        }
        service_response = self.client.post('/services',
            headers={"Authorization": f"Bearer {token}"},
            json=service_data
        )
        service_id = json.loads(service_response.data)['service']['id']

        # Create a vehicle
        token = self.get_token(self.user.username, "user123")
        vehicle_data = {
            "vehicle_name": "Test Car",
            "vehicle_model": "Test Model",
            "numberplate": f"TEST{uuid.uuid4().hex[:4]}",
            "vehicle_type": "car"
        }
        vehicle_response = self.client.post('/vehicles',
            headers={"Authorization": f"Bearer {token}"},
            json=vehicle_data
        )
        vehicle_id = json.loads(vehicle_response.data)['vehicle']['id']

        # Create booking
        booking_data = {
            "service_id": service_id,
            "vehicle_id": vehicle_id,
            "date": date.today().isoformat(),
            "time_from": "10:00",
            "time_to": "11:00",
            "payment_method": "stripe"
        }
        response = self.client.post('/bookings',
            headers={"Authorization": f"Bearer {token}"},
            json=booking_data
        )
        self.assertEqual(response.status_code, 201)

    def test_staff_update_booking(self):
        """Test staff updating booking status"""
        # Create booking first (reuse test_create_booking)
        self.test_create_booking()
        
        # Get booking ID
        token = self.get_token(self.user.username, "user123")
        bookings_response = self.client.get('/bookings',
            headers={"Authorization": f"Bearer {token}"}
        )
        booking_id = json.loads(bookings_response.data)['bookings'][0]['id']

        # Staff updates booking status
        staff_token = self.get_token(self.staff.username, "staff123")
        response = self.client.patch(f'/bookings/{booking_id}',
            headers={"Authorization": f"Bearer {staff_token}"},
            json={"status": "confirmed"}
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json.loads(response.data)['booking']['status'], 'confirmed')

if __name__ == '__main__':
    unittest.main() 