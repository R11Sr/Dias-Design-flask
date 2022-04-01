from flask import Blueprint
import os

from app import db, login_manager
from flask import render_template, request, redirect, url_for, flash,session
from flask_login import login_required
from flask_login import login_user, logout_user, current_user
from app.config import Config
from app.models import Product
from app.models import ProductTypes
from app.models import ProductColor
from app.forms import ProductForm
from app.models import UserProfile
from app.forms import LoginForm
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import  boto3
import botocore
import locale

locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' ) 
admin = Blueprint('admin',__name__)



@admin.route('/admin/manage_products')
@login_required
def admin_products():
    """Render the website's Admin Section."""

    if not session.get('admin'):
        flash("You are not Authorised to access that functionality",'warning')
        return redirect(url_for('public.home'))
        
    # all_products = Product.query.all()
    all_products = db.session.query(Product).order_by(Product.id)
    return render_template('mange_products.html', products = all_products)

@admin.route('/admin/add_product',methods=['GET','POST'])
@login_required
def add_product():
    """Render the  page to add a product."""

    if not session.get('admin'):
        flash("You are not Authorised to access that functionality",'warning')
        return redirect(url_for('public.home'))

    form = ProductForm()
    form.type_options.choices = [( option.value,option.name) for option in  ProductTypes]
    form.color_options.choices = [(option.value,option.name) for option in  ProductColor]

    if request.method == 'POST':
        if form.validate():
            price = form.price.data
            Description = form.Description.data.rstrip()
            title = form.title.data.rstrip()
            color = form.color_options.data
            type = form.type_options.data
            image = form.image.data
         
            # print(f"received from addprod Form: {price}, {title}, {Description}, { ProductColor(str(color))},{ProductTypes(str(type))},{image}")

            if image.filename == '':
                flash("No image has been selected",'warning')
                return redirect(request.url)
            
            imageName = secure_filename(image.filename.rstrip())

            image.save(str(os.path.join(Config.UPLOAD_FOLDER,imageName)))

            #check  to see if the image is already on the sever
            try:
                BUCKET_NAME = Config.BUCKET_NAME
                s3 = boto3.client(
                    's3',
                    aws_access_key_id = Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY)
                file = s3.get_object(Bucket = BUCKET_NAME,Key = imageName)
            
            #Save the image to the s3 bucket since  not there
            except botocore.exceptions.ClientError:
                BUCKET_NAME = Config.BUCKET_NAME
                s3 = boto3.resource('s3')
                imageData = open(str(os.path.join(Config.UPLOAD_FOLDER,imageName)),'rb')
                s3.Bucket(BUCKET_NAME).put_object(Key=imageName,Body=imageData)
            
            #Saves product to DB
            new_product  = Product(title,Description,ProductTypes(str(type)),price,ProductColor(str(color)),imageName)
            db.session.add(new_product)
            db.session.commit()
            
            flash(f"{title} Added to Catlog",'success')
            return redirect(url_for('admin.admin_products')) 
        else:
            print(form.errors)
            flash(form.errors)
            return redirect(request.url)

    return render_template('add_product.html', form = form)



@admin.route('/uploads/<imageName>')
def get_image(imageName):
    """Fetch Image from image server."""
    try:
        BUCKET_NAME = Config.BUCKET_NAME
        s3 = boto3.client(
            's3',
            aws_access_key_id = Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY)
        file = s3.get_object(Bucket = BUCKET_NAME,Key = imageName)

        return file['Body'].read()

    except botocore.exceptions.ClientError as error:
        flash(f'image {imageName} was not found')
        print(f"file: {imageName} not found!")
    return "File Not Found"
    


@admin.route('/admin/edit_product/<old_product_id>',methods=['GET','POST'])
@login_required
def edit_product(old_product_id):
    """Render the Edition page for a specific product."""

    if not session.get('admin'):
        flash("You are not Authorised to access that functionality",'warning')
        return redirect(url_for('public.home'))

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
            

            editing_object.price = price
            editing_object.Description = descrip
            editing_object.title = title
            editing_object.type = ProductTypes(str(type))
            editing_object.color = ProductColor(str(color))
            db.session.commit() # save data to DB

            flash("Product Updated!",'success')
            return redirect(url_for('admin.admin_products'))           
            
    # If the request is tp get the product to edit
    return render_template('edit_product.html',prod = editing_object, form = form)



@admin.route('/admin/delete_product_confirm/<invalid_product_id>')
@login_required
def confirm_deletion(invalid_product_id):
    """Removes Selected Product from the the Database after confirmation"""

    if not session.get('admin'):
        flash("You are not Authorised to access that functionality",'warning')
        return redirect(url_for('public.home'))


    delete_product=  Product.query.get(invalid_product_id) # fetches the product to delete
    db.session.delete(delete_product)
    db.session.commit()

    flash(f"Product {delete_product.title} Removed from Catalog",'warning')
    return redirect(url_for('admin.admin_products'))  


@admin.errorhandler(404)
def page_not_found(error):
    """Custom 404 page."""
    return render_template('404.html'), 404


@admin.errorhandler(500)
def internal_server_error(error):
    """Custom 500 page."""
    return render_template('500.html'), 500




# @admin.route("/admin/login", methods=["GET", "POST"])
# def login():
#     if current_user is not None and current_user.is_authenticated:
#         return redirect(url_for('public.home'))
#     form = LoginForm()
#     if request.method == "POST":
#         if form.validate():
#             email = form.email.data
#             pwrd = form.password.data
            
#             user = UserProfile.query.filter_by(email = email).first()
#             if user is not None and check_password_hash(user.password,pwrd):
#                 if email == 'admin@diasdesign.com':
#                     session['admin'] = True
#                 login_user(user)
#                 flash("Logged In Sucessfully",'success')
#                 next = request.args.get('next')
#                 return redirect(next or url_for("public.home")) 
#             else:
#                 flash("Incorrect credentials entered",'danger') 
#     flash_errors(form)
#     return render_template("login.html", form=form)

# @admin.route('/admin/logout')
# def logout():
#     logout_user()
#     session.clear()
#     flash('You were logged out', 'success')
#     return redirect(url_for('public.home'))

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



@admin.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 10 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response


