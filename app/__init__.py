from app.extensions import app, db
from app.models import User, Product, Category, ShoppingListItem

# Register blueprints
from app.auth.routes import auth
from app.main.routes import main

app.register_blueprint(auth, url_prefix='/auth')
app.register_blueprint(main)

# Create all tables
@app.before_first_request
def create_tables():
    db.create_all()

# Add default categories if none exist
@app.before_first_request
def add_default_categories():
    if Category.query.count() == 0:
        categories = [
            Category(name='Cleansers', description='Face wash, makeup removers, and cleansing balms'),
            Category(name='Moisturizers', description='Face creams, lotions, and hydrating products'),
            Category(name='Serums', description='Targeted treatment serums'),
            Category(name='Sunscreens', description='SPF and sun protection products'),
            Category(name='Masks', description='Face masks, sheet masks, and overnight treatments'),
            Category(name='Eye Care', description='Eye creams, serums, and treatments'),
            Category(name='Lip Care', description='Lip balms, treatments, and masks'),
            Category(name='Exfoliators', description='Chemical and physical exfoliants'),
            Category(name='Toners', description='Facial toners and essences'),
            Category(name='Foundation', description='Liquid, cream, and powder foundations'),
            Category(name='Concealer', description='Under-eye and blemish concealers'),
            Category(name='Powder', description='Setting and finishing powders'),
            Category(name='Blush', description='Cream and powder blushes'),
            Category(name='Bronzer', description='Bronzing and contouring products'),
            Category(name='Highlighter', description='Highlighting and illuminating products'),
            Category(name='Eye Shadow', description='Eye shadow palettes and singles'),
            Category(name='Eyeliner', description='Liquid, pencil, and gel eyeliners'),
            Category(name='Mascara', description='Lengthening and volumizing mascaras'),
            Category(name='Brow Products', description='Brow pencils, gels, and powders'),
            Category(name='Lipstick', description='Lipsticks, lip glosses, and lip liners'),
            Category(name='Setting Spray', description='Makeup setting and fixing sprays'),
            Category(name='Primer', description='Face and eye primers'),
            Category(name='Tools', description='Brushes, sponges, and other application tools'),
            Category(name='Other', description='Miscellaneous beauty products')
        ]
        
        for category in categories:
            db.session.add(category)
        
        db.session.commit()
