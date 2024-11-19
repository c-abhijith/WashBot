import unittest
import json
from app import create_app
from app.extensions import db
from app.models import User
from tests.config import TestConfig

class AuthTestCase(unittest.TestCase):
    def setUp(self):
        self.app = create_app()
        self.app.config.from_object(TestConfig)
        self.client = self.app.test_client()
        
        with self.app.app_context():
            db.create_all()
    
    def tearDown(self):
        with self.app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_signup_success(self):
        """Test successful user registration"""
        data = {
            "username": "testuser",
            "password": "testpass123",
            "phonenumber": "1234567890",
            "role": "user"
        }
        response = self.client.post('/signup', 
                                  data=json.dumps(data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 201)
        self.assertIn('User created', response.json['message'])
        
    def test_signup_duplicate_username(self):
        """Test signup with existing username"""
        data = {
            "username": "testuser",
            "password": "testpass123",
            "phonenumber": "1234567890",
            "role": "user"
        }
    
        self.client.post('/signup', 
                        data=json.dumps(data),
                        content_type='application/json')
        
    
        response = self.client.post('/signup', 
                                  data=json.dumps(data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Username already exists', response.json['message'])
    
    def test_signup_invalid_role(self):
        """Test signup with invalid role"""
        data = {
            "username": "testuser",
            "password": "testpass123",
            "phonenumber": "1234567890",
            "role": "invalid_role"
        }
        response = self.client.post('/signup', 
                                  data=json.dumps(data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid role', response.json['message'])
    
    def test_login_success(self):
        """Test successful login"""
        # Create user
        signup_data = {
            "username": "testuser",
            "password": "testpass123",
            "phonenumber": "1234567890",
            "role": "user"
        }
        self.client.post('/signup', 
                        data=json.dumps(signup_data),
                        content_type='application/json')
        
        # Login
        login_data = {
            "username": "testuser",
            "password": "testpass123"
        }
        response = self.client.post('/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)
        self.assertIn('refresh_token', response.json)
    
    def test_login_invalid_credentials(self):
        """Test login with invalid credentials"""
        login_data = {
            "username": "nonexistent",
            "password": "wrongpass"
        }
        response = self.client.post('/login', 
                                  data=json.dumps(login_data),
                                  content_type='application/json')
        self.assertEqual(response.status_code, 401)
        self.assertIn('Invalid username or password', response.json['message'])
    
    def test_refresh_token(self):
        """Test refresh token endpoint"""
        # First create and login a user
        signup_data = {
            "username": "testuser",
            "password": "testpass123",
            "phonenumber": "1234567890",
            "role": "user"
        }
        self.client.post('/signup', 
                        data=json.dumps(signup_data),
                        content_type='application/json')
        
        login_response = self.client.post('/login', 
                                        data=json.dumps({
                                            "username": "testuser",
                                            "password": "testpass123"
                                        }),
                                        content_type='application/json')
        
        refresh_token = login_response.json['refresh_token']
        
        # Test refresh endpoint
        response = self.client.post('/refresh',
                                  headers={'Authorization': f'Bearer {refresh_token}'})
        self.assertEqual(response.status_code, 200)
        self.assertIn('access_token', response.json)
    
    def test_protected_route(self):
        """Test protected route access"""
        # First create and login a user
        signup_data = {
            "username": "testuser",
            "password": "testpass123",
            "phonenumber": "1234567890",
            "role": "user"
        }
        self.client.post('/signup', 
                        data=json.dumps(signup_data),
                        content_type='application/json')
        
        login_response = self.client.post('/login', 
                                        data=json.dumps({
                                            "username": "testuser",
                                            "password": "testpass123"
                                        }),
                                        content_type='application/json')
        
        access_token = login_response.json['access_token']
        
        # Test protected endpoint
        response = self.client.get('/protected',
                                 headers={'Authorization': f'Bearer {access_token}'})
        self.assertEqual(response.status_code, 200)
    
    def test_protected_route_without_token(self):
        """Test protected route without token"""
        response = self.client.get('/protected')
        self.assertEqual(response.status_code, 401)

if __name__ == '__main__':
    unittest.main() 