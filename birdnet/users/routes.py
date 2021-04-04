from flask import Blueprint
from flask import render_template, session, request, redirect, url_for, abort
from datetime import datetime
from PIL import Image
import os 

from birdnet.models import User, Thread, Reply, BirdDetails, db
from birdnet import app, bcrypt, birdid_model
from birdnet.users.validations import validate_new_user, validate_details_for_updation, validate_password
from birdnet.users.utils import save_profile_photo

users = Blueprint('users', __name__)

# Registration Page 
@users.route("/register/", methods=['GET', 'POST'])
def register():
    if request.method == "POST":
        firstname = (request.form["firstname"]).strip() 
        lastname = (request.form["lastname"]).strip() 
        gender = (request.form["gender"]).strip() 
        email = (request.form["email"]).strip()  
        username = (request.form["username"]).strip()
        username = username.lower() 
        password = request.form["password"]
        reconfirmed_password = request.form["password-reconfirm"]

        errors = validate_new_user(firstname, lastname, gender, email, username, password, reconfirmed_password)

        if errors == {}:
            hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
            new_user = User(firstname = firstname, lastname = lastname,  gender = gender, 
                            email = email, username = username, password = hashed_password)
            db.session.add(new_user)
            db.session.commit()
            return render_template('users/register.html', title='Register', registration = "successful")
        else:
            return render_template('users/register.html', title='Register', errors = errors)
    elif request.method == "GET":
        if "username" in session:
            return redirect(url_for('users.profile'))
        return render_template('users/register.html', title='Register')

# Login and Register pages 
@users.route("/login/", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username = username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['profile-photo'] = user.profile_photo_path
            session['is-admin'] = user.is_admin
            return redirect(url_for('users.profile', username_param = username))
        elif user and password != user.password:
            return render_template('users/login.html', title='Login', login="incorrect_password")
        else:
            return render_template('users/login.html', title='Login', login="unsuccessful")
    elif request.method == "GET":
        if "username" in session:
            return redirect(url_for('users.profile', username_param = session['username']))
        return render_template('users/login.html', title='Login')

# Logout Page 
@users.route("/logout/")
def logout():
    session.pop('user_id')
    session.pop('username')
    session.pop('profile-photo')
    session.pop('is-admin')
    return redirect(url_for('users.login'))

# Profile Page 
@users.route("/profile/<username_param>", methods=['GET', 'POST'])
def profile(username_param):
    session_username = session.get("username")
    threads = Thread.query.order_by(Thread.creation_date.desc()).filter_by(username = username_param)
    user = User.query.filter_by(username = username_param).first()

    if user == None:
        abort(404)
    if username_param == session_username:
        if request.method == "POST":
            current_user = user

            firstname = (request.form["firstname"]).strip() 
            lastname = (request.form["lastname"]).strip() 
            gender = (request.form["gender"]).strip() 
            email = (request.form["email"]).strip()
            bio = request.form["bio"].strip()  
            username = (request.form["username"]).strip()
            username = username.lower()

            errors, current_user =  validate_details_for_updation(current_user, firstname, lastname, gender, email, username, bio)

            if request.files['profile-photo']:
                filename = save_profile_photo(current_user, request.files['profile-photo'])
                current_user.profile_photo_path = filename

            if errors == {}:
                db.session.add(current_user)
                db.session.commit()
                session['user_id'] = current_user.user_id
                session['username'] = current_user.username
                session['profile-photo'] = current_user.profile_photo_path
                session['is-admin'] = current_user.is_admin
                return render_template('users/profile.html', title='Profile', user = current_user, updation = "successful", recent_threads = threads)
            else:
                return render_template('users/profile.html', title='Profile', user = current_user, errors = errors, recent_threads = threads)         
        elif request.method == "GET":
            username = session["username"]
            current_user = user
            return render_template('users/profile.html', user = current_user, recent_threads = threads)
    else:
        if request.method == 'GET':
            requested_user = user
            return render_template('users/profile.html', user= requested_user, recent_threads = threads)
        elif request.method == 'POST':
            abort(403)

@users.route("/password_reset/", methods=['GET', 'POST'])
def password_reset():
    if request.method == 'POST':
        username = session['username']
        current_pwd = request.form["current_pwd"]
        new_pwd = request.form["new_pwd"]
        reconfirm_new_pwd = request.form["reconfirm_new_pwd"]
        user = User.query.filter_by(username = username).first()

        if user and bcrypt.check_password_hash(user.password, current_pwd):
            if new_pwd == reconfirm_new_pwd:
                if validate_password(new_pwd, reconfirm_new_pwd):
                    hashed_password = bcrypt.generate_password_hash(new_pwd).decode('utf-8')
                    user.password = hashed_password
                    db.session.add(user)
                    db.session.commit()
                    return render_template('users/password_reset.html', title='Reset Password', status="successful")
                else:
                    return render_template('users/password_reset.html', title='Reset Password', status="pwd_error_message")
            else:
                return render_template('users/password_reset.html', title='Reset Password', status="passwords_dont_match")
        else:
            return render_template('users/password_reset.html', title='Reset Password', status="incorrect_password")
    elif request.method == 'GET':
        if "username" in session:
            return render_template('users/password_reset.html')
        else:
            abort(404)

@users.route("/delete_account/", methods=['GET', 'POST'])
def delete_account():
    if request.method == 'POST':
        if "username" in session:
            username = request.form["username"]
            password = request.form["password"]
            retyped_password = request.form["retype-password"]
            if username == session['username'] and password == retyped_password:
                user = User.query.filter_by(username = username).first()
                if user and bcrypt.check_password_hash(user.password, password):
                    db.session.delete(user)
                    db.session.commit()
                    session.clear()
                    return render_template('users/delete_account.html', deletion=True)
                else:
                    return render_template('users/delete_account.html', errors=True)  
            else:
                return render_template('users/delete_account.html', errors=True)   
    elif request.method == 'GET':
        if "username" in session:
            return render_template('users/delete_account.html') 
        else:
            abort(404)

@users.route("/superadmin_panel/", methods=['GET', 'POST'])
def superadmin_panel():
    admin_users = User.query.filter_by(is_admin = True).all()
    if request.method == "POST":

        if request.form["type"] == "grant-rights":
            new_admin_username = request.form["new-admin"]

            NewAdminUser = User.query.filter_by(username = new_admin_username).first()
            if NewAdminUser != None:
                NewAdminUser.is_admin = True
                db.session.add(NewAdminUser)
                db.session.commit()
                admin_users = User.query.filter_by(is_admin = True).all()
                return render_template("users/superadmin_panel.html", status="user-made-admin", new_admin_user = NewAdminUser, admin_users = admin_users)
            else:
                return render_template("users/superadmin_panel.html", status="user-does-not-exist", new_admin_user = new_admin_username, admin_users = admin_users)

        elif request.form["type"] == "revoke-rights":
            revoke_admin_username = request.form["revoke-admin-rights"]
            RevokeAdminUser = User.query.filter_by(username = revoke_admin_username).first()
            if RevokeAdminUser != None:
                RevokeAdminUser.is_admin = False
                db.session.add(RevokeAdminUser)
                db.session.commit()
                admin_users = User.query.filter_by(is_admin = True).all()
                return render_template("users/superadmin_panel.html", status="admin-rights-revoked", revoke_admin_user = RevokeAdminUser, admin_users = admin_users)
            else:
                return render_template("users/superadmin_panel.html", status="user-to-be-revoked-does-not-exist", revoke_admin_user = revoke_admin_username, admin_users = admin_users)
    
    elif request.method == "GET":
        if "username" in session:
            if session["username"] == "admin" or session["username"] == "superadmin":
                return render_template("users/superadmin_panel.html", admin_users = admin_users)
            else:
                abort(404)
            