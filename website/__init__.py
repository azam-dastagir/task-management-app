from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from os import path
from flask_login import LoginManager
import os
import secrets
secret_key = secrets.token_hex(16)  # Generates a 32-character hexadecimal secret key
from dotenv import find_dotenv,load_dotenv
from flask_mail import Mail,Message



load_dotenv(find_dotenv())

mail_password = os.environ.get('PASSWORD')


db = SQLAlchemy()
login_manager = LoginManager()
mail = Mail()

app = Flask(__name__)



def create_app():
    
    app.secret_key = 'Azam'

    
    app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:8106328334@localhost/demo'
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
    
    #Configure flask-Mail for Gmail
    app.config['MAIL_SERVER'] = 'smtp.gmail.com'
    app.config['MAIL_PORT'] = 587
    app.config['MAIL_USE_TLS'] = True
    app.config['MAIL_USE_SSL'] = False
    app.config['MAIL_USERNAME'] = 'sdgiri0662@gmail.com'
    app.config['MAIL_PASSWORD'] = 'cclwfpwvrpmstzng'
    app.config['MAIL_DEFAULT_SENDER'] = 'sdgiri0662@gmail.com'


    
    db.__init__(app)
    login_manager.login_view = "auth.login"
    login_manager.init_app(app)
    mail.__init__(app)

    with app.app_context():
        print("Creating database tables...")
        db.create_all(app=app)
        print("Database tables created successfully.")

    from .auth import auth
    from .views import views
    from .models import User

    @login_manager.user_loader
    def load_user(id):
        return User.query.get(int(id))
    

    app.register_blueprint(auth, url_prefix = '/')
    app.register_blueprint(views, url_prefix = '/')

    return app