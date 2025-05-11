import unittest
from flask import url_for
from app.extensions import app, db, bcrypt
from app.models import User, Product, Category, ShoppingListItem
from datetime import datetime, timedelta

class MainTestCase(unittest.TestCase):
    """Test case for main functionality."""
    
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
            
            # Create test category
            test_category = Category(
                name='Test Category',
                description='Test Description'
            )
            db.session.add(test_category)
            
            # Create test product
            test_product = Product(
                name='Test Product',
                brand='Test Brand',
                description='Test Description',
                purchase_date=datetime.now().date(),
                expiration_date=datetime.now().date() + timedelta(days=30),
                date_opened=datetime.now().date(),
                price=10.99,
                user_id=1,
                category_id=1
            )
            db.session.add(test_product)
            
            # Create test shopping list item
            test_item = ShoppingListItem(
                product_name='Test Item',
                brand='Test Brand',
                notes='Test Notes',
                priority=2,
                user_id=1
            )
            db.session.add(test_item)
            
            db.session.commit()
            
            # Login the test user
            self.app.post('/login', data={
                'email': 'test@example.com',
                'password': 'testpassword'
            })
    
    def tearDown(self):
        """Clean up after tests."""
        with app.app_context():
            db.session.remove()
            db.drop_all()
    
    def test_dashboard_access(self):
        """Test accessing dashboard."""
        response = self.app.get('/dashboard')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Dashboard', response.data)
    
    def test_products_list(self):
        """Test accessing products list."""
        response = self.app.get('/products')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'My Products', response.data)
        self.assertIn(b'Test Product', response.data)
    
    def test_add_product(self):
        """Test adding a new product."""
        response = self.app.post('/products/add', data={
            'name': 'New Product',
            'brand': 'New Brand',
            'description': 'New Description',
            'category_id': 1,
            'purchase_date': datetime.now().date(),
            'price': 15.99
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Product added successfully', response.data)
        self.assertIn(b'New Product', response.data)
    
    def test_view_product(self):
        """Test viewing a product."""
        response = self.app.get('/products/1')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Test Product', response.data)
        self.assertIn(b'Test Brand', response.data)
    
    def test_categories_list(self):
        """Test accessing categories list."""
        response = self.app.get('/categories')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Categories', response.data)
        self.assertIn(b'Test Category', response.data)
    
    def test_add_category(self):
        """Test adding a new category."""
        response = self.app.post('/categories/add', data={
            'name': 'New Category',
            'description': 'New Description'
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Category added successfully', response.data)
        self.assertIn(b'New Category', response.data)
    
    def test_shopping_list(self):
        """Test accessing shopping list."""
        response = self.app.get('/shopping-list')
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Shopping List', response.data)
        self.assertIn(b'Test Item', response.data)
    
    def test_add_shopping_item(self):
        """Test adding a new shopping item."""
        response = self.app.post('/shopping-list/add', data={
            'product_name': 'New Item',
            'brand': 'New Brand',
            'notes': 'New Notes',
            'priority': 3
        }, follow_redirects=True)
        
        self.assertEqual(response.status_code, 200)
        self.assertIn(b'Item added to shopping list', response.data)
        self.assertIn(b'New Item', response.data)