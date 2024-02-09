from flask import Blueprint,request
from .models import User
from . import db
from flask_login import login_required,login_user,logout_user
from werkzeug.security import generate_password_hash, check_password_hash

auth = Blueprint('auth',__name__)

@auth.route('/')
def home():
    return "This is Home"
@auth.route('/register')
def register():
    username = request.form.get('username')
    email = request.form.get('email')
    password = request.form.get('password')
    cnfm_password = request.form.get('cnfm_password')

    if password != cnfm_password:
        return "Passwords do not match"
    else:
        new_user = User(username=username,email=email,password=generate_password_hash(password,method="sha256"))
        db.session.add(new_user)
        db.session.commit()
        return "User Added Successfully"

@auth.route('/login',methods = ['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        curr_user = User.query.filter_by(username=username).first()
        if curr_user:
            if check_password_hash(curr_user.password, password):
                login_user(user=curr_user)
                return f"Welcome {curr_user.username}, to the Task Manager"
            else:
                return "Wrong password, please try again!"
        else:
            return "User does not exist, please register first!"
    else:
        return "This is a GET request, change it to POST to login"

    
@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return "User has been logged out"
