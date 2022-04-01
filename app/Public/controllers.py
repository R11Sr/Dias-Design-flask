"""
Flask Documentation:     http://flask.pocoo.org/docs/
Jinja2 Documentation:    http://jinja.pocoo.org/2/documentation/
Werkzeug Documentation:  http://werkzeug.pocoo.org/documentation/
This file creates your application.
"""
from flask import Blueprint

from crypt import methods
from app import app, db, login_manager
from flask import render_template, request, redirect, url_for, flash,session
from flask_login import login_user, logout_user, current_user
from app.forms import LoginForm
from app.models import Product, UserProfile

from app.forms import AccountForm
from app import db
from werkzeug.security import check_password_hash



public = Blueprint('public',__name__)



###
# Routing for your application.
###

@public.route('/')
def home():
    """Render website's home page."""
    return render_template('home.html')


@public.route('/about/')
def about():
    """Render the website's about page."""
    return render_template('about.html')


@public.route('/products')
def browse_products():
    """Allows a visitor to browse product catalog"""
    listOfProducts = Product.query.all()
    return render_template('productsCatalog.html',productList = listOfProducts)

@public.route('/create_account',methods=['POST',"GET"])
def create_account():
    """Visitor uses this to create an account for the application"""

    # ensure an authenticated user is not able to create an account
    if current_user is not None and current_user.is_authenticated:
        return redirect(url_for('public.home'))
    
    form = AccountForm()

    if request.method == 'POST':
        if form.validate():
            firstName = form.firstName.data.capitalize().rstrip()
            lastName = form.lastName.data.capitalize().rstrip()
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
                return redirect(next or url_for("public.home"))
            flash("Passwords do not match!",'danger')
        flash_errors(form)
    
    return render_template("create_account.html", form=form)


@public.route("/login", methods=["GET", "POST"])
def login():
    """Visitor uses this to Authorise and Authenticate themselves"""

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
                return redirect(next or url_for("public.home")) 
            else:
                flash("Incorrect credentials entered",'danger') 
    flash_errors(form)
    return render_template("login.html", form=form)

@public.route('/logout')
def logout():
    """Logout of the application"""

    logout_user()
    session.clear()
    flash('You were logged out', 'success')
    return redirect(url_for('public.home'))

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


@public.route('/<file_name>.txt')
def send_text_file(file_name):
    """Send your static text file."""
    file_dot_text = file_name + '.txt'
    return app.send_static_file(file_dot_text)


@public.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


@public.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


if __name__ == '__main__':
    app.run(debug=True, host="0.0.0.0", port="8080")
