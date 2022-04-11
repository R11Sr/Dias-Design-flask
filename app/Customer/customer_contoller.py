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
from app.models import Product, UserProfile,ShoppingCart,Order
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

@customer.route('/profile')
def profile():
    """Renders the user profile with the pertinent Order data"""

    itemNames={}
    itemPrices = {}
    c_uid = current_user.get_id()
    orders = Order.query.filter(Order.customer_id == c_uid).all()

    for order in orders:
        prod_id = order.product_id
        itemNames[order.id] = Product.query.filter(Product.id == prod_id).first().title
        itemPrices[order.id] = Product.query.filter(Product.id == prod_id).first().price
        
    
    

    return render_template('customer_pages/profile.html',orders = orders, itemNames = itemNames, itemPrices = itemPrices, locale = locale)


@customer.route('/place-order')
def place_order():
    """Places the order for that customer"""
    u_id = current_user.get_id()
    
    lineItems = ShoppingCart.query.filter(ShoppingCart.customer_id == u_id)

    for lineItem in lineItems:
        c_uid = current_user.get_id()
        price  = Product.query.filter(Product.id == lineItem.product_id).first().price
        total = lineItem.quantity * price
        status = 'pending'
        order = Order(c_uid,lineItem.product_id,lineItem.quantity,total,status)

        db.session.add(order)
        db.session.commit()

    for lineItem in lineItems:
        db.session.delete(lineItem)
        db.session.commit()

    # return redirect(url_for('customer.profile'))
    return redirect(url_for('public.browse_products'))

            

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


@customer.route('/set-cart-amount',methods=['POST'])
def get_cart_amount():
    """function to return the amount of items in current user's cart"""
    ##################
    # Interesting section here. used the request object to get the actual 
    # bytes passed and usd string manipulation to gety the user ID
    ##################
    
    data = request.get_data()
    data = data.decode('utf-8')
    
    _  = data.find('=')
    u_id = data[_:][1:]

    lineItems = 0 

    #fetchs the amount of items for user
    user_items = ShoppingCart.query.filter(ShoppingCart.customer_id == u_id)
    
    for item in user_items:
        lineItems+= item.quantity

    return jsonify({'lineItems':lineItems})


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


@customer.errorhandler(500)
def internal_server_error(error):
    """Custom 500 page."""
    return render_template('500.html'), 500

    