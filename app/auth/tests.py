import unittest
from flask import url_for
from app.extensions import app, db, bcrypt
from app.models import User

class AuthTestCase(unittest.TestCase):
    """Test case for authentication functionality."""
    
    def setUp(self):
        """Set up test environment."""
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        
        with app.app_context():
            db.create_all()
            
            # Create test user
            hashed_password = bcrypt.generate_password_hash('testpassword').decode('utf-8')
            test_user = User(
                username='testuser',
                email='test@example.com',
                password=hashed_password
            )
            db.session.add(test_user)
            db.session.commit()
    
    def tearDown(self):
        """Clean up after tests."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_signup_page(self):
        """Test accessing signup page."""
        response = self.app.get('/signup')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Sign Up', response.data)
    
    def test_login_page(self):
        """Test accessing login page."""
        response = self.app.get('/login')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Log In', response.data)
    
    def test_signup(self):
        """Test user signup."""
        response = self.app.post('/signup', data={
            'username': 'newuser',
            'email': 'new@example.com',
            'password': 'newpassword',
            'confirm_password': 'newpassword'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Your account has been created!', response.data)
        
        # Check if user was added to database
        with app.app_context():
            user = User.query.filter_by(username='newuser').first()
            self.assertIsNotNone(user)
    
    def test_login(self):
        """Test user login."""
        response = self.app.post('/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)  # Assuming dashboard shows after login
    
    def test_login_invalid(self):
        """Test login with invalid credentials."""
        response = self.app.post('/login', data={
            'email': 'test@example.com',
            'password': 'wrongpassword'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Login failed', response.data)
    
    def test_logout(self):
        """Test user logout."""
        # First login
        self.app.post('/login', data={
            'email': 'test@example.com',
            'password': 'testpassword'
        })
        
        # Then logout
        response = self.app.get('/logout', follow_redirects=True)
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'You have been logged out', response.data)