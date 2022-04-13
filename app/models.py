from datetime import date
from itertools import product
from . import db
import enum
from werkzeug.security import generate_password_hash

class UserProfile(db.Model):
    # You can use this to change the table name. The default convention is to use
    # the class name. In this case a class name of UserProfile would create a
    # user_profile (singular) table, but if we specify __tablename__ we can change it
    # to `user_profiles` (plural) or some other name.
    __tablename__ = 'user_profiles'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80))
    last_name = db.Column(db.String(80))
    email = db.Column(db.String(128), unique=True)
    password = db.Column(db.String(255))

    def __init__(self,first_name,last_name,email,password):
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.password = generate_password_hash(password,method='pbkdf2:sha256')
        # date joined


    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        try:
            return unicode(self.id)  # python 2 support
        except NameError:
            return str(self.id)  # python 3 support

    def __repr__(self):
        return f"<User: {self.email}, id: {self.id} >"

class ProductTypes(enum.Enum):
    Accessories ='Accessories'
    Tops = 'Tops'
    Bikini_and_Coverup = 'Bikini & Coverup'
    swimsuits = 'swimsuits'

class ProductColor(enum.Enum):
    red = 'Red'
    green = 'Green'
    blue = 'Blue'
    purple = 'Purple'
    orange = 'Orange'
    yellow = 'Yellow'
    multi_colored= 'Multi-coloured'
    white = 'White'

class OrderStatus(enum.Enum):
    paid = 'Paid'
    pending = 'pending'
    processing= 'In Progress'
    completed = 'Completed'
    delivering = 'Out-for-delvery'
    delivered = 'Delivered'
    cancelled = 'Cancelled'




class Product(db.Model):
    __tablename__ = 'products'
    
    id = db.Column(db.Integer, primary_key=True)
    title =  db.Column(db.String(80),  nullable  = False)
    Description =  db.Column(db.String(2048))
    type = db.Column(db.Enum(ProductTypes),default = ProductTypes.Tops, nullable  = False)
    price = db.Column(db.Numeric(8,2),nullable  = False) # will change this to currency
    color = db.Column(db.Enum(ProductColor))
    image = db.Column(db.String(256))
    
    def __init__(self,title,Description,type,price,color,image):
        super().__init__()
        self.title = title
        self.Description = Description
        self.type = type
        self.price = price
        self.color = color
        self.image = image
    
    # These methods to splice off the unwanted part of the Enum selected
    #they are called on the object in the respective views
    def get_type(self):
        type = str(self.type).split('.')
        return type[1]

    def get_color(self):
        color = str(self.color).split('.')
        return color[1]

    def __repr__(self):
        return f"<{self.id},{self.title},{self.type},{self.price}>"

class ShoppingCart(db.Model):
    __tablename__='shopping-cart'

    id= db.Column(db.Integer, primary_key=True)
    customer_id=db.Column(db.Integer,nullable=False)
    product_id=db.Column(db.Integer,nullable= False)
    quantity = db.Column(db.Numeric,nullable =False)

    def __init__(self,customer_id,product_id,quantity):
        super().__init__()
        self.customer_id = customer_id
        self.product_id = product_id
        self.quantity = quantity

    def __repr__(self):
        return f"<id: {self.id}, cust_id: {self.customer_id}>"

class Order(db.Model):
    __tablename__ = 'orders'

    id = db.Column(db.Integer,primary_key =True)
    customer_id = db.Column(db.Integer,nullable=False)
    product_id=db.Column(db.Integer,nullable= False)
    quantity=db.Column(db.Integer,nullable= False)
    total = db.Column(db.Numeric(8,2),nullable  = False)
    status = db.Column(db.Enum(OrderStatus))

    def __init__(self,customer_id,product_id,quantity,total,status):
        super().__init__()
        self.customer_id = customer_id
        self.product_id = product_id
        self.quantity = quantity
        self.total = total
        self.status = status

    def __repr__(self):
        return f"< Order Id: {self.id}, Status: {self.status}>"

    def get_status(self):
       _ = str(self.status).split('.')
       return _[1]