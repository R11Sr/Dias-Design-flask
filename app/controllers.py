"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""

from crypt import methods
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash,session
from flask_login import login_user, logout_user, current_user, login_required
from app.forms import LoginForm
from app.models import UserProfile
from app.models import Product
from app.models import ProductTypes
from app.models import ProductColor
from app.forms import ProductForm
from app.forms import AccountForm
from app import db
from werkzeug.security import check_password_hash



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
@login_required
def admin_products():
    """Render the website's Admin Section."""
    if not session.get('admin'):
        flash("You are not Authorised to access that functionality",'warning')
        return redirect(url_for('home'))
        
    # all_products = Product.query.all()
    all_products = db.session.query(Product).order_by(Product.id)
    return render_template('mange_products.html', products = all_products)

@app.route('/add_product',methods=['GET','POST'])
@login_required
def add_product():
    """Render the  page to add a product."""
    if not session.get('admin'):
        flash("You are not Authorised to access that functionality",'warning')
        return redirect(url_for('home'))

    form = ProductForm()
    form.type_options.choices = [( option.value,option.name) for option in  ProductTypes]
    form.color_options.choices = [(option.value,option.name) for option in  ProductColor]

    if request.method == 'POST':
        if form.validate():
            price = form.price.data
            Description = form.Description.data
            title = form.title.data
            color = form.color_options.data
            type = form.type_options.data

            # Debugging output
            # print(f"received from addprod Form: {price}, {title}, {Description}, { ProductColor(str(color))},{ProductTypes(str(type))}")

            new_product  = Product(title,Description,ProductTypes(str(type)),price,ProductColor(str(color)))
            db.session.add(new_product)
            db.session.commit()
            
            flash(f"{title} Added to Catlog",'success')
            return redirect(url_for('admin_products'))  

    return render_template('add_product.html', form = form)



@app.route('/edit_product/<old_product_id>',methods=['GET','POST'])
@login_required
def edit_product(old_product_id):
    """Render the Edition page for a specific product."""
    if not session.get('admin'):
        flash("You are not Authorised to access that functionality",'warning')
        return redirect(url_for('home'))

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



@app.route('/delete_product_confirm/<invalid_product_id>')
@login_required
def confirm_deletion(invalid_product_id):
    """Removes Selected Product from the the Database after confirmation"""
    if not session.get('admin'):
        flash("You are not Authorised to access that functionality",'warning')
        return redirect(url_for('home'))


    delete_product=  Product.query.get(invalid_product_id) # fetches the product to delete
    db.session.delete(delete_product)
    db.session.commit()

    flash(f"Product {delete_product.title} Removed from Catalog",'warning')
    return redirect(url_for('admin_products'))  


@app.route('/create_account',methods=['POST',"GET"])
def create_account():
    """Visitor uses this to create an account for the application"""

    # ensure an authenticated user is not able to create an account
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = AccountForm()

    if request.method == 'POST':
        if form.validate():
            firstName = form.firstName.data.capitalize()
            lastName = form.lastName.data.capitalize()
            email = form.email.data
            password = form.password.data
            retypePassword = form.retypePassword.data

            print(f"user data: fname:{firstName}, lname{lastName}, email:{email}")

            if password == retypePassword:
                user = UserProfile(firstName,lastName,email,password)
                db.session.add(user)
                db.session.commit()

                flash('Account Sucessfully Created!','success')
                next = request.args.get('next')
                return redirect(next or url_for("home"))
            flash("Passwords do not match!",'danger')
        flash_errors(form)
    
    return render_template("create_account.html", form=form)






@app.route("/login", methods=["GET", "POST"])
def login():
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if request.method == "POST":
        if form.validate():
            email = form.email.data
            pwrd = form.password.data
            
            user = UserProfile.query.filter_by(email = email).first()
            if user is not None and check_password_hash(user.password,pwrd):
                if email == 'admin@diasdesign.com':
                    session['admin'] = True
                login_user(user)
                flash("Logged In Sucessfully",'success')
                next = request.args.get('next')
                return redirect(next or url_for("home")) 
            else:
                flash("Incorrect credentials entered",'danger') 
    flash_errors(form)
    return render_template("login.html", form=form)

@app.route('/logout')
def logout():
    logout_user()
    flash('You were logged out', 'success')
    return redirect(url_for('home'))

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
