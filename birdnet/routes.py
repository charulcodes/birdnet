from flask import render_template, session, request, redirect, url_for, abort
from datetime import datetime

from birdnet.models import User, Thread, Reply, BirdDetails, db
from birdnet import app, bcrypt
from birdnet.validations import validate_new_user, validate_details_for_updation, validate_password, validate_new_thread, validate_thread_for_updation, validate_reply_for_updation
from birdnet.utils import save_profile_photo, save_thread_photo, save_reply_photo


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
def login(delete_param = None):
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = User.query.filter_by(username = username).first()
        if user and bcrypt.check_password_hash(user.password, password):
            session['user_id'] = user.user_id
            session['username'] = user.username
            session['profile-photo'] = user.profile_photo_path
            if delete_param == True:
                return redirect(url_for('delete_account'))
            else:
                return redirect(url_for('profile', username_param = username))
        elif user and password != user.password:
            return render_template('login.html', title='Login', login="incorrect_password")
        else:
            return render_template('login.html', title='Login', login="unsuccessful")
    elif request.method == "GET":
        if ("username" in session) and delete_param == True:
            return render_template('login.html', title='Login', delete_param = True) 
        elif "username" in session:
            return redirect(url_for('profile', username_param = session['username']))
        return render_template('login.html', title='Login')

# Logout Page 
@app.route("/logout/")
def logout():
    session.pop('user_id')
    session.pop('username')
    session.pop('profile-photo')
    return redirect(url_for('login'))

# Profile Page 
@app.route("/profile/<username_param>", methods=['GET', 'POST'])
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
                return render_template('profile.html', title='Profile', user = current_user, updation = "successful", recent_threads = threads)
            else:
                return render_template('profile.html', title='Profile', user = current_user, errors = errors, recent_threads = threads)         
        elif request.method == "GET":
            username = session["username"]
            current_user = user
            return render_template('profile.html', user = current_user, recent_threads = threads)
    else:
        if request.method == 'GET':
            requested_user = user
            return render_template('profile.html', user= requested_user, recent_threads = threads)
        elif request.method == 'POST':
            abort(403)

@app.route("/password_reset/", methods=['GET', 'POST'])
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
                    return render_template('password_reset.html', title='Reset Password', status="successful")
                else:
                    return render_template('password_reset.html', title='Reset Password', status="pwd_error_message")
            else:
                return render_template('password_reset.html', title='Reset Password', status="passwords_dont_match")
        else:
            return render_template('password_reset.html', title='Reset Password', status="incorrect_password")
    elif request.method == 'GET':
        if "username" in session:
            return render_template('password_reset.html')
        else:
            abort(404)

@app.route("/delete_account/", methods=['GET', 'POST'])
def delete_account(relogin = None):
    if request.method == 'POST':
        if relogin == True:
            return render_template('delete_account.html', status = "successful")
    elif request.method == 'GET':
        if "username" in session:
            return login(delete_param = True)
        elif relogin == True:
            return render_template('delete_account.html') 
        else:
            abort(404)

# ------------------------------------ FORUM ------------------------------------
@app.route("/forum/", methods=['GET', 'POST'])
def forum():
    if request.method == 'POST':
        title = request.form["thread-title"].strip()
        caption = request.form["thread-caption"].strip()
        username = session['username']
        filename = None

        if request.files['thread-image']:
            filename = save_thread_photo(request.files['thread-image'])

        errors = validate_new_thread(title, caption)

        if errors == {}:
            thread = Thread(username=username, title=title, caption=caption, image_path=filename, view_count=0)
            db.session.add(thread)
            db.session.commit()
            new_threads = Thread.query.order_by(Thread.creation_date.desc()).all()
            return render_template('forum.html', title='Forum', status="successful", new_threads = new_threads)
        else:
            new_threads = Thread.query.all()
            return render_template('forum.html', title='Forum', status="unsuccessful", errors= errors, new_threads = new_threads)
    elif request.method == 'GET':
        new_threads = Thread.query.order_by(Thread.creation_date.desc()).all()
        return render_template('forum.html', title='Forum', new_threads = new_threads)

# Post 
@app.route("/forum/thread/<thread_id>", methods=['GET', 'POST'])
def thread(thread_id):
    thread = Thread.query.get_or_404(thread_id)
    replies = Reply.query.filter_by(thread_id = thread.thread_id).order_by(Reply.creation_date.desc()).all()
    if request.method == 'POST':
        if request.form['form-type'] == 'create-reply':
            username = session['username']
            reply_caption = request.form["reply-caption"].strip()
            filename = None

            if request.files['reply-image']:
                filename = save_reply_photo(request.files['reply-image'])
                
            errors = {}
            if reply_caption == '':
                errors['reply_caption'] = 'Please enter text in the reply.'
            elif len(reply_caption) > 400:
                errors['reply_caption'] = 'Reply cannot be longer than 400 characters.'

            if errors == {}:
                new_reply = Reply(username = username, caption = reply_caption, image_path = filename, thread_id = thread.thread_id)
                db.session.add(new_reply)
                db.session.commit()
                replies = Reply.query.filter_by(thread_id = thread.thread_id).order_by(Reply.creation_date.desc()).all()
                return render_template('thread.html', thread = thread, replies = replies, status = 'reply-creation-successful')
            else:
                errors['reply-creation'] = True
                return render_template('thread.html', thread = thread, replies = replies, errors = errors, status = 'reply-creation-failed')
        elif request.form['form-type'] == 'edit-thread':
            username = session['username']
            thread_title = request.form["thread-title"].strip()
            thread_caption = request.form["thread-caption"].strip()
            thread_id = int(request.form["thread-id"])
            filename = None

            if request.files['thread-image']:
                filename = save_thread_photo(request.files['thread-image'])
                
            thread = Thread.query.get(reply_id)
            errors, thread = validate_thread_for_updation(thread, thread_title, thread_caption)

            if errors == {}:
                db.session.add(thread)
                db.session.commit()
                replies = Reply.query.filter_by(thread_id = thread.thread_id).order_by(Reply.creation_date.desc()).all()
                return render_template('thread.html', thread = thread, replies = replies, status = 'thread-updation-successful')
            else:
                errors['thread-id'] = thread_id
                return render_template('thread.html', thread = thread, replies = replies, errors = errors, status = 'thread-updation-failed')
        elif request.form['form-type'] == 'edit-reply':
            username = session['username']
            reply_caption = request.form["reply-caption"].strip()
            reply_id = int(request.form["reply-id"])
            filename = None

            if request.files['reply-image']:
                filename = save_reply_photo(request.files['reply-image'])
                
            reply = Reply.query.get(reply_id)
            errors, reply = validate_reply_for_updation(reply, reply_caption)

            if errors == {}:
                db.session.add(reply)
                db.session.commit()
                replies = Reply.query.filter_by(thread_id = thread.thread_id).order_by(Reply.creation_date.desc()).all()
                return render_template('thread.html', thread = thread, replies = replies, status = 'reply-updation-successful')
            else:
                errors['reply-id'] = reply_id
                return render_template('thread.html', thread = thread, replies = replies, errors = errors, status = 'reply-updation-failed')
        elif request.form['form-type'] == 'delete-thread':
            pass
        elif request.form['form-type'] == 'delete-reply':
            pass
    elif request.method == 'GET':
        return render_template('thread.html', thread = thread, replies = replies)

@app.route("/forum/threads/", methods=['GET', 'POST'])   
def all_threads():
    pass 

# Search for a forum post
@app.route("/forum/search/")
def post_search():
    return render_template('post_search.html')
