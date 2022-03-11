"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm
from app.models import UserProfile
from app.models import Product
from app.models import ProductTypes
from app.models import ProductColor
from app.forms import ProductForm
from app import db



###
# Routing for your application.
###

@app.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@app.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')

@app.route('/manage_products')
def admin_products():
    """Render the website's Admin Section."""
    all_products = Product.query.all()
    return render_template('mange_products.html', products = all_products)

@app.route('/edit_product/<old_product_id>',methods=['GET','POST'])
def edit_product(old_product_id):
    """Render the Edition page for a specific product."""
    editing_object=  Product.query.filter_by(id=old_product_id).first() # fetches the product to edit

    form = ProductForm(color_options=editing_object.color.value, type_options =editing_object.type.value) # pre-selects the type and color in form
    form.type_options.choices = [( option.value,option.name) for option in  ProductTypes]
    form.color_options.choices = [(option.value,option.name) for option in  ProductColor]

    # IF the request is to submit the form
    if request.method == "POST" :
        if form.validate():
            price = form.price.data
            descrip = form.Description.data
            title = form.title.data
            color = form.color_options.data
            type = form.type_options.data
            
            #Debugging output
            # print(f"received from Form: {price}, {title}, {descrip}, { ProductColor(str(color))},{ProductTypes(str(type))}")

            editing_object.price = price
            editing_object.Description = descrip
            editing_object.title = title
            editing_object.type = ProductTypes(str(type))
            editing_object.color = ProductColor(str(color))
            db.session.commit() # save data to DB

            flash("Product Updated!",'success')
            return redirect(url_for('admin_products'))           
            
    # If the request is tp get the product to edit
    return render_template('edit_product.html',prod = editing_object, form = form)

    
    


@app.route("/login", methods=["GET", "POST"])
def login():
    form = LoginForm()
    if request.method == "POST":
        # change this to actually validate the entire form submission
        # and not just one field
        if form.username.data:
            # Get the username and password values from the form.

            # using your model, query database for a user based on the username
            # and password submitted. Remember you need to compare the password hash.
            # You will need to import the appropriate function to do so.
            # Then store the result of that query to a `user` variable so it can be
            # passed to the login_user() method below.

            # get user id, load into session
            login_user(user)

            # remember to flash a message to the user
            return redirect(url_for("home"))  # they should be redirected to a secure-page route instead
    return render_template("login.html", form=form)


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


@app.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@app.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")
