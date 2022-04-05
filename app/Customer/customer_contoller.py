"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""
from flask import Blueprint

from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash,session
from flask_login import login_user, logout_user, current_user
from app.forms import LoginForm
from app.models import Product, UserProfile

from app.forms import AccountForm
from app import db
from werkzeug.security import check_password_hash

import locale
locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )

customer = Blueprint('customer',__name__)

@customer.route('/cart')
def shopping_cart():
    """Render Shopping Cart."""
    pass
@customer.route('/place-order')
def place_order():
    """Places the order for that customer"""
    pass