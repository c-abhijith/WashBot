import unittest
import json
from app import create_app, db
from app.models import User, Service
from app.helper.auth_helper import password_hash
import uuid

class ServiceTestCase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app()
        cls.app.config['TESTING'] = True
        cls.app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:postgres@localhost:5432/washbot_test"
        cls.client = cls.app.test_client()
        
        # Create application context
        cls.app_context = cls.app.app_context()
        cls.app_context.push()
        
        # Create all tables
        db.create_all()

    @classmethod
    def tearDownClass(cls):
        db.session.remove()
        db.drop_all()
        cls.app_context.pop()

    def setUp(self):
        # Clear all tables before each test
        db.session.query(Service).delete()
        db.session.query(User).delete()
        db.session.commit()
        
        # Create unique usernames for each test run
        unique_id = str(uuid.uuid4())[:8]
        
        # Create test admin user
        admin = User(
            username=f"admin_test_{unique_id}",
            password=password_hash("admin123"),
            phonenumber="1234567890",
            role="admin"
        )
        
        # Create test regular user
        user = User(
            username=f"user_test_{unique_id}",
            password=password_hash("user123"),
            phonenumber="9876543210",
            role="user"
        )
        
        # Create test service
        self.test_service_name = f"Test Service {unique_id}"
        service = Service(
            service_name=self.test_service_name,
            description="Test Description",
            price=99.99,
            duration=60,
            vehicle_type="car"
        )
        
        db.session.add(admin)
        db.session.add(user)
        db.session.add(service)
        db.session.commit()
        
        # Store test IDs and usernames
        self.admin_id = str(admin.id)
        self.user_id = str(user.id)
        self.service_id = str(service.id)
        self.admin_username = admin.username
        self.user_username = user.username
    
    def tearDown(self):
        # Clear data after each test
        db.session.query(Service).delete()
        db.session.query(User).delete()
        db.session.commit()

    def get_admin_token(self):
        """Helper method to get admin token"""
        response = self.client.post('/login',
            json={
                "username": self.admin_username,
                "password": "admin123"
            }
        )
        data = json.loads(response.data)
        return data['accessToken']
    
    def get_user_token(self):
        """Helper method to get user token"""
        response = self.client.post('/login',
            json={
                "username": self.user_username,
                "password": "user123"
            }
        )
        data = json.loads(response.data)
        return data['accessToken']

    def test_get_services_public(self):
        """Test getting services list"""
        response = self.client.get('/services')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertIn('services', data)
        self.assertTrue(len(data['services']) > 0)

    def test_get_service_detail(self):
        """Test getting single service detail"""
        response = self.client.get(f'/services/{self.service_id}')
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['service']['service_name'], self.test_service_name)

    def test_create_service_admin(self):
        """Test creating service as admin"""
        token = self.get_admin_token()
        service_data = {
            "service_name": "New Service",
            "description": "New Description",
            "price": 149.99,
            "duration": 90,
            "vehicle_type": "car"
        }
        
        response = self.client.post('/services',
            headers={"Authorization": f"Bearer {token}"},
            json=service_data
        )
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(data['service']['service_name'], service_data['service_name'])

    def test_create_service_unauthorized(self):
        """Test creating service as regular user"""
        token = self.get_user_token()
        service_data = {
            "service_name": "Unauthorized Service",
            "description": "Test Description",
            "price": 99.99,
            "duration": 60,
            "vehicle_type": "car"
        }
        
        response = self.client.post('/services',
            headers={"Authorization": f"Bearer {token}"},
            json=service_data
        )
        
        self.assertEqual(response.status_code, 403)

    def test_update_service_admin(self):
        """Test updating service as admin"""
        token = self.get_admin_token()
        update_data = {
            "service_name": "Updated Service",
            "price": 199.99
        }
        
        response = self.client.put(f'/services/{self.service_id}',
            headers={"Authorization": f"Bearer {token}"},
            json=update_data
        )
        
        data = json.loads(response.data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(data['service']['service_name'], update_data['service_name'])

    def test_delete_service_admin(self):
        """Test deleting service as admin"""
        token = self.get_admin_token()
        response = self.client.delete(f'/services/{self.service_id}',
            headers={"Authorization": f"Bearer {token}"}
        )
        
        self.assertEqual(response.status_code, 200)
        
        # Verify deletion
        get_response = self.client.get(f'/services/{self.service_id}')
        self.assertEqual(get_response.status_code, 404)

if __name__ == '__main__':
    unittest.main() 