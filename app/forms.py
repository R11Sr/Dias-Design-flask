from itertools import product
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField,TextAreaField,SelectField
from wtforms.validators import InputRequired, DataRequired
from app.models import ProductColor


class LoginForm(FlaskForm):
    username = StringField('Username', validators=[InputRequired()])
    password = PasswordField('Password', validators=[InputRequired()])



class ProductForm(FlaskForm):
    title = StringField('title', validators=[InputRequired()])
    Description = TextAreaField('Description',validators=[DataRequired()])
    price= StringField('price', validators=[InputRequired()])
    color_options= SelectField('color',validators=[DataRequired()])
    type_options = SelectField('type',validators=[DataRequired()])   