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
from app.models import Product, UserProfile,ShoppingCart
from sqlalchemy import select

from app.forms import RegistrationForm
from app import db
from werkzeug.security import check_password_hash

import locale
locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' )

customer = Blueprint('customer',__name__)

@customer.route('/cart')
def view_shopping_cart():
    """Render Shopping Cart."""
    pass

@customer.route('/place-order')
def place_order():
    """Places the order for that customer"""
    pass

@customer.route('/add-to-cart/<prod_id>')
def add_to_cart(prod_id):

    c_uid = current_user.id
    item_check = ShoppingCart.query.filter(ShoppingCart.product_id == prod_id).filter(ShoppingCart.customer_id == c_uid).first()

    # increment the quantity of the item in the cart if present 
    # else put item in cart
    if item_check is not None:
        item_check.quantity +=1
        db.session.commit()
    else:
        line_item = ShoppingCart(c_uid,prod_id,1)
        db.session.add(line_item)
        db.session.commit()

    redirect(url_for('public.browse_products'))
    