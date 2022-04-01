from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from .config import Config
from flask_migrate import Migrate
# import boto3


app = Flask(__name__)


app.config.from_object(Config)

db = SQLAlchemy(app)

migrate = Migrate(app,db)

# Flask-Login login manager
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'controllers.login'
login_manager.blueprint_login_views = {
    'admin' : '/admin/login',
    'public' : '/login'
}

from .Admin.admin_controller import admin
from .Public.controllers import public

app.register_blueprint(admin)
app.register_blueprint(public)


# from app import controllers
