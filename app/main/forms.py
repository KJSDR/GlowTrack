from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, SubmitField, FloatField, DateField, SelectField, IntegerField
from wtforms.validators import DataRequired, Optional

class ProductForm(FlaskForm):
    """Form for adding and editing products."""
    
    name = StringField('Product Name', validators=[DataRequired()])
    brand = StringField('Brand', validators=[Optional()])
    description = TextAreaField('Description', validators=[Optional()])
    category_id = SelectField('Category', coerce=int, validators=[DataRequired()])
    purchase_date = DateField('Purchase Date', format='%Y-%m-%d', validators=[Optional()])
    expiration_date = DateField('Expiration Date', format='%Y-%m-%d', validators=[Optional()])
    date_opened = DateField('Date Opened', format='%Y-%m-%d', validators=[Optional()])
    period_after_opening = IntegerField('Period After Opening (months)', validators=[Optional()])
    price = FloatField('Price', validators=[Optional()])
    image = FileField('Product Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png'], 'Images only!')
    ])
    submit = SubmitField('Save Product')


class CategoryForm(FlaskForm):
    """Form for adding and editing categories."""
    
    name = StringField('Category Name', validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    submit = SubmitField('Save Category')


class ShoppingListItemForm(FlaskForm):
    """Form for adding items to shopping list."""
    
    product_name = StringField('Product Name', validators=[DataRequired()])
    brand = StringField('Brand', validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    priority = SelectField('Priority', 
                          choices=[(1, 'Low'), (2, 'Medium'), (3, 'High')],
                          coerce=int,
                          validators=[DataRequired()])
    submit = SubmitField('Add to Shopping List')