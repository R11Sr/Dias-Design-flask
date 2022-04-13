from itertools import product
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,TextAreaField,SelectField
from wtforms.validators import InputRequired, DataRequired
from app.models import ProductColor
from flask_wtf.file import FileField, FileAllowed,FileRequired


class LoginForm(FlaskForm):
    email = StringField('email', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])



class ProductForm(FlaskForm):
    title = StringField('Title', validators=[InputRequired()])
    Description = TextAreaField('Description',validators=[DataRequired()])
    price= StringField('Price', validators=[InputRequired()])
    color_options= SelectField('Color',validators=[DataRequired()])
    type_options = SelectField('Type',validators=[DataRequired()])  
    image = FileField('Image',validators=[FileRequired(),FileAllowed(['jpg','png','jpeg'],'Select image files only.')])

    
class UpdateOrder(FlaskForm):
    status_options= SelectField('status',validators=[DataRequired()])

class UploadInvoice(FlaskForm):
    invoice = FileField('invoice',validators=[FileRequired(),FileAllowed(['pdf'],'Please Select the Invoice in PDF format')])

class RegistrationForm(FlaskForm):
    firstName = StringField('First Name', validators=[InputRequired()])
    lastName = StringField('Last Name', validators=[InputRequired()])
    email = StringField('Email', validators=[InputRequired()])
    password = StringField('Password', validators=[InputRequired()])
    retypePassword = StringField('Re-enter Password', validators=[InputRequired()])