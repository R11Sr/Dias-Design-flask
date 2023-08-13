from crypt import methods
from urllib.parse import urldefrag
from flask import Blueprint, jsonify,json, send_from_directory
import os

from app import db, login_manager, app
from flask import render_template, request, redirect, url_for, flash,session,make_response,abort
from flask_login import login_required
from flask_login import login_user, logout_user, current_user
from app.config import Config
from app.models import Product
from app.models import ProductTypes 
from app.models import ProductColor
from app.models import OrderStatus
from app.forms import ProductForm, UpdateOrder,UploadInvoice
from app.models import UserProfile, Order
from app.forms import LoginForm
from werkzeug.security import check_password_hash
from werkzeug.utils import secure_filename
import  boto3 # python adapter for AWS S3 Service
import botocore # python adapter for AWS S3 Service
import locale
import pdfkit # produces PDF from information stored on orders in the DB

locale.setlocale( locale.LC_ALL, 'en_CA.UTF-8' ) 
admin = Blueprint('admin',__name__) # load the admin blueprint

"""All Print statements are for debugging purposes"""

@admin.route('/admin/manage_products')
@login_required
def admin_products():
    """Render the website's Admin Section."""

    if not session.get('admin'):
        flash("You are not Authorised to access that functionality",'warning')
        return redirect(url_for('public.home'))
        
    # all_products = Product.query.all()
    all_products = db.session.query(Product).order_by(Product.id)
    return render_template('manage_products.html', products = all_products)


@admin.route('/generate-invoice/<orderID>')
@login_required
def generate_invoice(orderID):
    """Generates an invoice for a selected Order"""

    # instructions were found here: https://www.youtube.com/watch?v=C8jxInLM9nM
    # used the aux tool here: https://github.com/JazzCore/python-pdfkit/wiki/Using-wkhtmltopdf-without-X-server

    orderInfo = Order.query.filter(Order.id ==orderID).first()
    prodTitle = Product.query.filter(Product.id == orderInfo.product_id).first().title
    prodPrice = Product.query.filter(Product.id == orderInfo.product_id).first().price
    cust = UserProfile.query.filter(UserProfile.id == orderInfo.customer_id).first()
    
    order = {
        'id': orderID,
        'custName': f"{cust.first_name} {cust.last_name}",
        'custContact': f"{cust.email}",
        'itemTitle': prodTitle,
        'quantity': orderInfo.quantity,
        'price': prodPrice,
        'status': orderInfo.get_status(),
        'total': orderInfo.total
        }

    #produces a PDF that is viewed in the browser
    rendered = render_template('admin_pages/invoice_template.html',order = order,locale = locale)
    pdf = pdfkit.from_string(rendered,False)
    response = make_response(pdf)
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename=Dias-Design-Inv-{orderInfo.id}.pdf' 
    return response

@admin.route('/get-invoice/<invoiceName>')
@login_required
def view_invoice(invoiceName):
    """fetch the Invoice from the S3 Storage Server."""

    try:
        BUCKET_NAME = Config.BUCKET_NAME
        s3 = boto3.client(
            's3',
            aws_access_key_id = Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY)
        file = s3.get_object(Bucket = BUCKET_NAME,Key = invoiceName)
        
        response = make_response(file['Body'].read())
        response.headers['Content-Type'] = 'application/pdf'
        response.headers['Content-Disposition'] = f'inline; filename={invoiceName}' 

        return response

    except botocore.exceptions.ClientError as error:
        flash(f'Invoice {invoiceName} was not found')
        print(f"file: {invoiceName} not found!")
    return redirect(request.url)    


@admin.route('/upload-invoice/<orderID>',methods=['GET','POST'])
@login_required
def upload_invoice(orderID):
    """Used to upload the Invoice for a specific Order 
    So that the customer can have it visable"""
    form = UploadInvoice()

    if request.method == 'POST':
        if form.validate():
            invoice = form.invoice.data

            invoiceName = secure_filename(invoice.filename.rstrip())
            invoice.save(str(os.path.join(Config.UPLOAD_FOLDER,invoiceName)))

             #check  to see if the Invoice is already on the sever

            try:
                BUCKET_NAME = Config.BUCKET_NAME
                s3 = boto3.client(
                    's3',
                    aws_access_key_id = Config.AWS_ACCESS_KEY_ID,
                    aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY)
                file = s3.get_object(Bucket = BUCKET_NAME,Key = invoiceName)
                    
                #Save the image to the s3 bucket since  not there
            except botocore.exceptions.ClientError:
                BUCKET_NAME = Config.BUCKET_NAME
                s3 = boto3.resource('s3')
                invoiceData = open(str(os.path.join(Config.UPLOAD_FOLDER,invoiceName)),'rb')
                s3.Bucket(BUCKET_NAME).put_object(Key=invoiceName,Body=invoiceData)
                
                flash(f"{invoiceName} Uploaded",'success')
                return redirect(url_for('admin.view_orders')) 
        else:
            flash(form.errors,'warning')
            return redirect(request.url)
    
    return render_template('admin_pages/upload_invoice.html',form = form,orderID = orderID)
    
                

@admin.route('/manage-orders')
@login_required
def view_orders():
    """Renders a List of All orders"""

    itemNames={}
    itemPrices = {}
    productsImage = {}
    orders = Order.query.all()

    for order in orders:
        prod_id = order.product_id
        product =  Product.query.filter(Product.id == prod_id).first()
        itemNames[order.id] =product.title
        itemPrices[order.id] = product.price 
        productsImage[order.id] = product.image


    return render_template('admin_pages/manage_orders.html',orders = orders, itemNames = itemNames, itemPrices = itemPrices, productsImage = productsImage, locale = locale)



@admin.route('/manage-orders/<orderID>',methods=['GET','POST'])
@login_required
def order_details(orderID):
    """Exposes the order details for a specific order and allows 
    an admin to manage it"""
    
    orderInfo = Order.query.filter(Order.id ==orderID).first()
    prodTitle = Product.query.filter(Product.id == orderInfo.product_id).first().title
    cust = UserProfile.query.filter(UserProfile.id == orderInfo.customer_id).first()

    invoiceStatus = 'disabled' # disables the invoice status until the checks are made to ensure one exists
    
    invoiceName = f'Dias-Design-Inv-{orderInfo.id}.pdf'
    if invoiceAvailable(invoiceName):
        invoiceStatus = 'enabled'
    order = {
        'id': orderID,
        'custName': f"{cust.first_name} {cust.last_name}",
        'custContact': f"{cust.email}",
        'itemTitle': prodTitle,
        'quantity': orderInfo.quantity,
        'status': orderInfo.get_status(),
        'total': orderInfo.total,
        'invoice': invoiceStatus,
        'invoiceName':invoiceName
        }
    
    form = UpdateOrder(status_options = orderInfo.status.value) # pre-selects the status for the drop down option
    
    # passes all the options of order status to the form
    form.status_options.choices = [(option.value,option.name) for option in OrderStatus] 

    # Save updated status to the db
    if request.method  =='POST':
        if form.validate():
            status = form.status_options.data
            orderInfo.status = OrderStatus(str(status))
            print(orderInfo) 
            db.session.commit()
            
            flash('Order status updated!','success')
            redirect(url_for('admin.view_orders'))
        else:
            print(form.errors)
            flash(form.errors)
            return redirect(request.url)
    
    return render_template('admin_pages/order_details.html',order = order,locale = locale, form = form )

""""Aux Function"""
@admin.route('/invoiceAvailable')
@login_required
def invoiceAvailable(invoiceName):
    """returns a boolean to see if an invoice exists on the S3 storage server"""
    try:
        BUCKET_NAME = Config.BUCKET_NAME
        s3 = boto3.client(
            's3',
            aws_access_key_id = Config.AWS_ACCESS_KEY_ID,
            aws_secret_access_key = Config.AWS_SECRET_ACCESS_KEY)
        file = s3.get_object(Bucket = BUCKET_NAME,Key = invoiceName)

        return True

    except botocore.exceptions.ClientError as error:
        pass
    return False



@admin.route('/admin/add_product',methods=['GET','POST'])
@login_required
def add_product():
    """Render the  page to add a product. Only enabled if the user is an admin"""

    if not session.get('admin'):
        flash("You are not Authorised to access that functionality",'warning')
        return redirect(url_for('public.home'))

    form = ProductForm()
    form.type_options.choices = [( option.value,option.name) for option in  ProductTypes] #load the product types in the form
    form.color_options.choices = [(option.value,option.name) for option in  ProductColor] #load the color types in the form

    if request.method == 'POST':
        if form.validate():
            price = form.price.data
            Description = form.Description.data.rstrip()
            title = form.title.data.rstrip()
            color = form.color_options.data
            type = form.type_options.data
            image = form.image.data
         

            #if no images are selected returns to the previous page
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
        
    #if request method is GET, load the form
    return render_template('add_product.html', form = form)


"""Aux Function"""

@admin.route('/image-server/<imageName>')
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
    

@admin.route('/get-logo/<logoName>')
def getLogo(logoName):
    """Fetch logo from static folder"""
    try: 
        return send_from_directory(os.path.join(os.getcwd(),app.config['STATIC_IMAGES_FOLDER']),logoName)
    except FileNotFoundError:
        abort(404)



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
            
    # If the request is GET show the product to edit
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


