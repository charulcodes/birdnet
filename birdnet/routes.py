from flask import render_template, session, request, redirect, url_for
from datetime import datetime

from birdnet.models import User, db
from birdnet import app, bcrypt
from birdnet.validations import validate_new_user, validate_details_for_updation
from birdnet.utils import save_profile_photo


# ------------------------------------ HOME & ABOUT PAGES ------------------------------------
@app.route("/")
def index():
    return render_template('index.html')

@app.route("/about/")
def about():
    return render_template('about.html')


# ------------------------------------ TOOLS ------------------------------------
@app.route("/birdid/")
def birdid():
    return render_template('birdid.html', title='Bird Identification')

@app.route("/search/")
def search():
    return render_template('search.html')


# ------------------------------------ ERROR PAGES ------------------------------------
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404

# Registration Page 
@app.route("/register/", methods=['GET', 'POST'])
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
            return render_template('register.html', title='Register', registration = "successful")
        else:
            return render_template('register.html', title='Register', errors = errors)
    elif request.method == "GET":
        if "username" in session:
            return redirect(url_for('profile'))
        return render_template('register.html', title='Register')

# Login and Register pages 
@app.route("/login/", methods=['GET', 'POST'])
def login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username = username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['profile-photo'] = user.profile_photo_path
            return redirect(url_for('profile'))
        elif user and password != user.password:
            return render_template('login.html', title='Login', login="incorrect_password")
        else:
            return render_template('login.html', title='Login', login="unsuccessful")
    elif request.method == "GET":
        if "username" in session:
            return redirect(url_for('profile'))
        return render_template('login.html', title='Login')

# Logout Page 
@app.route("/logout/")
def logout():
    session.pop('user_id')
    session.pop('username')
    session.pop('profile-photo')
    return redirect(url_for('login'))

# Profile Page 
@app.route("/profile/", methods=['GET', 'POST'])
def profile():
    if request.method == "POST":
        session_username = session["username"]
        current_user = User.query.filter_by(username = session_username).first()

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
            return render_template('profile.html', title='Profile', user = current_user, updation = "successful")
        else:
            return render_template('profile.html', title='Profile', user = current_user, errors = errors)
                
    elif request.method == "GET":
        if "username" in session:
            username = session["username"]
            current_user = User.query.filter_by(username = username).first()
            return render_template('profile.html', user = current_user)
        else:
            return redirect(url_for('login'))


# ------------------------------------ FORUM ------------------------------------
@app.route("/forum/")
def forum():
    return render_template('forum.html', title='Forum')

# Post 
@app.route("/post/")
def post():
    return render_template('post.html')

# Search for a forum post
@app.route("/forum/search/")
def post_search():
    return render_template('post_search.html')

