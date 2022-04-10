"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""
from crypt import methods
from flask import Blueprint, jsonify

from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash,session
from flask_login import login_required, login_user, logout_user, current_user
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
    itemNames ={}
    itemPrices ={}

    c_uid = current_user.get_id()
    lineItems = ShoppingCart.query.filter(ShoppingCart.customer_id == c_uid).all()

    for item in lineItems:
        prod = Product.query.filter(Product.id == item.product_id).first()
        name = prod.title
        price = prod.price
        itemNames[item.id] = name
        itemPrices[item.id] = price

    return render_template('customer_pages/cart.html',lineItems = lineItems,itemNames = itemNames, itemPrices = itemPrices)

@customer.route('/place-order')
def place_order():
    """Places the order for that customer"""
    pass

@customer.route('/add-to-cart', methods=['POST'])
@login_required
def add_to_cart():
    """Adds Item to customer database"""
    total = 0
    
    prod_id = request.form['prod_id']
    print(f'received ID: {prod_id}')
    

    #commits the item to the shopping cart
    c_uid = current_user.get_id()
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


    #fetchs the amount of items for user
    user_items = ShoppingCart.query.filter(ShoppingCart.customer_id == c_uid)
    
    for item in user_items:
        total+= item.quantity

    return jsonify({'cart':total})


# user_loader callback. This callback is used to reload the user object from
# the user ID stored in the session
@login_manager.user_loader
def load_user(id):
    return UserProfile.query.get(int(id))

###
# The functions below should be applicable to all Flask apps.
###

# Flash errors from the form if validation fails
def flash_errors(form):
    for field, errors in form.errors.items():
        for error in errors:
            flash(u"Error in the %s field - %s" % (
                getattr(form, field).label.text,
                error
            ), 'danger')


@customer.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@customer.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@customer.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404

    