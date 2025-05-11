from app.extensions import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    """User model for authentication."""
    
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    date_joined = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    products = db.relationship('Product', back_populates='user', cascade='all, delete-orphan')
    shopping_list_items = db.relationship('ShoppingListItem', back_populates='user', cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<User {self.username}>'


class Category(db.Model):
    """Category model for organizing products."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    
    # Relationships
    products = db.relationship('Product', back_populates='category')
    
    def __repr__(self):
        return f'<Category {self.name}>'


class Product(db.Model):
    """Product model for skincare and makeup items."""
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100))
    description = db.Column(db.Text)
    purchase_date = db.Column(db.Date)
    expiration_date = db.Column(db.Date)
    date_opened = db.Column(db.Date)
    period_after_opening = db.Column(db.Integer, default=12)  # Months
    price = db.Column(db.Float)
    image_url = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    
    # Relationships
    user = db.relationship('User', back_populates='products')
    category = db.relationship('Category', back_populates='products')
    
    def __repr__(self):
        return f'<Product {self.name}>'
    
    def is_expired(self):
        """Check if product is expired."""
        if self.expiration_date:
            return datetime.now().date() > self.expiration_date
        return False
    
    def days_until_expiration(self):
        """Calculate days until expiration."""
        if self.expiration_date:
            delta = self.expiration_date - datetime.now().date()
            return delta.days
        return None


class ShoppingListItem(db.Model):
    """Shopping list model for tracking products to purchase."""
    
    id = db.Column(db.Integer, primary_key=True)
    product_name = db.Column(db.String(100), nullable=False)
    brand = db.Column(db.String(100))
    notes = db.Column(db.Text)
    priority = db.Column(db.Integer, default=1)  # 1=Low, 2=Medium, 3=High
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Foreign Keys
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Relationships
    user = db.relationship('User', back_populates='shopping_list_items')
    
    def __repr__(self):
        return f'<ShoppingListItem {self.product_name}>'