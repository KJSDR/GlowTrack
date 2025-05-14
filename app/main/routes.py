from flask import Blueprint, render_template, redirect, url_for, flash, request, current_app
from flask_login import current_user, login_required
from app.models import Product, Category, ShoppingListItem
from app.main.forms import ProductForm, CategoryForm, ShoppingListItemForm
from app.extensions import db
import os
from datetime import datetime, timedelta
from werkzeug.utils import secure_filename
import uuid

def ensure_upload_folder_exists():
    """Make sure the upload folder exists."""
    upload_folder = os.path.join('app', 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder

main = Blueprint('main', __name__)

@main.route('/')
def index():
    """Display the home page."""
    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    return render_template('main/index.html', title='Welcome to GlowTrack')


@main.route('/dashboard')
@login_required
def dashboard():
    """Display the user dashboard."""
    # Get counts
    product_count = Product.query.filter_by(user_id=current_user.id).count()
    category_count = Category.query.count()
    shopping_list_count = ShoppingListItem.query.filter_by(user_id=current_user.id).count()
    
    # Get soon-to-expire products (within 30 days)
    thirty_days_from_now = datetime.now().date() + timedelta(days=30)
    expiring_soon = Product.query.filter(
        Product.user_id == current_user.id,
        Product.expiration_date.isnot(None),
        Product.expiration_date <= thirty_days_from_now,
        Product.expiration_date >= datetime.now().date()
    ).order_by(Product.expiration_date).limit(5).all()
    
    # Get recently added products
    recent_products = Product.query.filter_by(user_id=current_user.id).order_by(
        Product.created_at.desc()
    ).limit(5).all()
    
    # Get shopping list high priority items
    high_priority_items = ShoppingListItem.query.filter_by(
        user_id=current_user.id, 
        priority=3
    ).order_by(ShoppingListItem.created_at.desc()).limit(5).all()
    
    return render_template(
        'main/dashboard.html',
        title='Dashboard',
        product_count=product_count,
        category_count=category_count,
        shopping_list_count=shopping_list_count,
        expiring_soon=expiring_soon,
        recent_products=recent_products,
        high_priority_items=high_priority_items
    )


# PRODUCT ROUTES
@main.route('/products')
@login_required
def products():
    """Display all products for the current user."""
    products = Product.query.filter_by(user_id=current_user.id).order_by(Product.name).all()
    return render_template('main/products/index.html', products=products, title='My Products')


@main.route('/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    """Handle adding a new product."""
    form = ProductForm()
    
    # Populate category choices
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
    
    if form.validate_on_submit():
        image_filename = None
        
        # Handle image upload if provided
        if form.image.data:
            image_file = form.image.data
            # Create unique filename
            filename = secure_filename(f"{uuid.uuid4()}_{image_file.filename}")
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            # Ensure directory exists
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            
            # Save the file
            image_file.save(image_path)
            image_filename = filename
        
        # Create new product
        product = Product(
            name=form.name.data,
            brand=form.brand.data,
            description=form.description.data,
            category_id=form.category_id.data,
            purchase_date=form.purchase_date.data,
            expiration_date=form.expiration_date.data,
            date_opened=form.date_opened.data,
            period_after_opening=form.period_after_opening.data,
            price=form.price.data,
            image_url=image_filename,
            user_id=current_user.id
        )
        
        db.session.add(product)
        db.session.commit()
        
        flash('Product added successfully!', 'success')
        return redirect(url_for('main.products'))
    
    return render_template('main/products/add.html', form=form, title='Add Product')


@main.route('/products/<int:id>')
@login_required
def view_product(id):
    """Display a product's details."""
    product = Product.query.get_or_404(id)
    
    # Check if the product belongs to the current user
    if product.user_id != current_user.id:
        flash('You do not have permission to view this product.', 'danger')
        return redirect(url_for('main.products'))
    
    return render_template('main/products/view.html', product=product, title=product.name)


@main.route('/products/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(id):
    """Handle editing a product."""
    product = Product.query.get_or_404(id)
    
    # Check if the product belongs to the current user
    if product.user_id != current_user.id:
        flash('You do not have permission to edit this product.', 'danger')
        return redirect(url_for('main.products'))
    
    form = ProductForm()
    
    # Populate category choices
    form.category_id.choices = [(c.id, c.name) for c in Category.query.order_by(Category.name).all()]
    
    if form.validate_on_submit():
        # Update product details
        product.name = form.name.data
        product.brand = form.brand.data
        product.description = form.description.data
        product.category_id = form.category_id.data
        product.purchase_date = form.purchase_date.data
        product.expiration_date = form.expiration_date.data
        product.date_opened = form.date_opened.data
        product.period_after_opening = form.period_after_opening.data
        product.price = form.price.data
        
        # Handle image upload if provided
        if form.image.data:
            # Delete old image if exists
            if product.image_url:
                old_image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_url)
                if os.path.exists(old_image_path):
                    os.remove(old_image_path)
            
            # Save new image
            image_file = form.image.data
            filename = secure_filename(f"{uuid.uuid4()}_{image_file.filename}")
            image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            
            os.makedirs(os.path.dirname(image_path), exist_ok=True)
            image_file.save(image_path)
            
            product.image_url = filename
        
        db.session.commit()
        
        flash('Product updated successfully!', 'success')
        return redirect(url_for('main.view_product', id=product.id))
    
    # Populate form with existing data
    elif request.method == 'GET':
        form.name.data = product.name
        form.brand.data = product.brand
        form.description.data = product.description
        form.category_id.data = product.category_id
        form.purchase_date.data = product.purchase_date
        form.expiration_date.data = product.expiration_date
        form.date_opened.data = product.date_opened
        form.period_after_opening.data = product.period_after_opening
        form.price.data = product.price
    
    return render_template('main/products/edit.html', form=form, product=product, title='Edit Product')


@main.route('/products/<int:id>/delete', methods=['POST'])
@login_required
def delete_product(id):
    """Handle deleting a product."""
    product = Product.query.get_or_404(id)
    
    # Check if the product belongs to the current user
    if product.user_id != current_user.id:
        flash('You do not have permission to delete this product.', 'danger')
        return redirect(url_for('main.products'))
    
    # Delete product image if exists
    if product.image_url:
        image_path = os.path.join(current_app.config['UPLOAD_FOLDER'], product.image_url)
        if os.path.exists(image_path):
            os.remove(image_path)
    
    db.session.delete(product)
    db.session.commit()
    
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('main.products'))


# CATEGORY ROUTES
@main.route('/categories')
@login_required
def categories():
    """Display categories."""
    categories = Category.query.order_by(Category.name).all()
    return render_template('main/categories/index.html', categories=categories, title='Categories')


@main.route('/categories/add', methods=['GET', 'POST'])
@login_required
def add_category():
    """Handle adding a new category."""
    form = CategoryForm()
    
    if form.validate_on_submit():
        # Create new category
        category = Category(
            name=form.name.data,
            description=form.description.data
        )
        
        db.session.add(category)
        db.session.commit()
        
        flash('Category added successfully!', 'success')
        return redirect(url_for('main.categories'))
    
    return render_template('main/categories/add.html', form=form, title='Add Category')


@main.route('/categories/<int:id>/edit', methods=['GET', 'POST'])
@login_required
def edit_category(id):
    """Handle editing a category."""
    category = Category.query.get_or_404(id)
    
    form = CategoryForm()
    
    if form.validate_on_submit():
        # Update category details
        category.name = form.name.data
        category.description = form.description.data
        
        db.session.commit()
        
        flash('Category updated successfully!', 'success')
        return redirect(url_for('main.categories'))
    
    # Populate form with existing data
    elif request.method == 'GET':
        form.name.data = category.name
        form.description.data = category.description
    
    return render_template('main/categories/edit.html', form=form, category=category, title='Edit Category')


@main.route('/categories/<int:id>/delete', methods=['POST'])
@login_required
def delete_category(id):
    """Handle deleting a category."""
    category = Category.query.get_or_404(id)
    
    # Check if category has associated products
    if category.products:
        flash('Cannot delete category with associated products.', 'danger')
        return redirect(url_for('main.categories'))
    
    db.session.delete(category)
    db.session.commit()
    
    flash('Category deleted successfully!', 'success')
    return redirect(url_for('main.categories'))


# SHOPPING LIST ROUTES
@main.route('/shopping-list')
@login_required
def shopping_list():
    """Display shopping list for the current user."""
    shopping_list = ShoppingListItem.query.filter_by(user_id=current_user.id).order_by(
        ShoppingListItem.priority.desc(), ShoppingListItem.created_at.desc()
    ).all()
    
    form = ShoppingListItemForm()
    
    return render_template(
        'main/shopping_list/index.html', 
        shopping_list=shopping_list, 
        form=form,
        title='Shopping List'
    )


@main.route('/shopping-list/add', methods=['POST'])
@login_required
def add_shopping_item():
    """Handle adding item to shopping list."""
    form = ShoppingListItemForm()
    
    if form.validate_on_submit():
        item = ShoppingListItem(
            product_name=form.product_name.data,
            brand=form.brand.data,
            notes=form.notes.data,
            priority=form.priority.data,
            user_id=current_user.id
        )
        
        db.session.add(item)
        db.session.commit()
        
        flash('Item added to shopping list!', 'success')
    
    return redirect(url_for('main.shopping_list'))


@main.route('/shopping-list/<int:id>/delete', methods=['POST'])
@login_required
def delete_shopping_item(id):
    """Handle deleting item from shopping list."""
    item = ShoppingListItem.query.get_or_404(id)
    
    # Check if the item belongs to the current user
    if item.user_id != current_user.id:
        flash('You do not have permission to delete this item.', 'danger')
        return redirect(url_for('main.shopping_list'))
    
    db.session.delete(item)
    db.session.commit()
    
    flash('Item removed from shopping list!', 'success')
    return redirect(url_for('main.shopping_list'))


@main.route('/shopping-list/<int:id>/toggle-priority', methods=['POST'])
@login_required
def toggle_priority(id):
    """Handle toggling priority of shopping list item."""
    item = ShoppingListItem.query.get_or_404(id)
    
    # Check if the item belongs to the current user
    if item.user_id != current_user.id:
        flash('You do not have permission to modify this item.', 'danger')
        return redirect(url_for('main.shopping_list'))
    
    # Cycle through priorities: 1 -> 2 -> 3 -> 1
    item.priority = item.priority % 3 + 1
    
    db.session.commit()
    
    return redirect(url_for('main.shopping_list'))