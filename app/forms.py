from itertools import product
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,TextAreaField,SelectField
from wtforms.validators import InputRequired, DataRequired


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])



class ProductForm(FlaskForm):
    # types = ProductTypes()
    title = StringField('title', validators=[InputRequired()])
    Description = TextAreaField('Description',validators=[DataRequired()])
    color_options= SelectField('color')
    type_options = SelectField('type')
    price= StringField('price', validators=[InputRequired()])
    