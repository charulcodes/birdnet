from flask import render_template, session, request, redirect, url_for, abort
from datetime import datetime
from sqlalchemy import or_, func

from birdnet.models import User, Thread, Reply, BirdDetails, db
from birdnet import app, bcrypt
from birdnet.validations import validate_new_user, validate_details_for_updation, validate_password, validate_new_thread, validate_thread_for_updation, validate_reply_for_updation, validate_description_for_bird_details
from birdnet.utils import save_profile_photo, save_thread_photo, save_reply_photo, save_bird_photo


# ------------------------------------ HOME & ABOUT PAGES ------------------------------------
@app.route("/")
def index():
    random_bird = BirdDetails.query.order_by(func.random()).first()
    return render_template('index.html', bird = random_bird)


@app.route("/about/")
def about():
    return render_template('about.html')


# ------------------------------------ TOOLS ------------------------------------
@app.route("/birdid/")
def birdid():
    return render_template('birdid.html', title='Bird Identification')

@app.route("/search/", methods=['GET','POST'])
def search():
    if request.method == 'POST':
       bird = request.form['search-query'].strip().title()
       bird = bird.replace(' ','-')
       
       if bird != "":
           results = BirdDetails.query.filter(
               or_(
                   BirdDetails.bird_name.contains(bird),
                   BirdDetails.scientific_name.contains(bird)
                   )).all()
       else:
           results = None

       return render_template('search.html', bird_data = results)
    elif request.method == 'GET':
       return render_template('search.html')

@app.route("/search/Edit/<bird_id>",methods=['GET','POST'])
def edit_bird(bird_id):
    if ("username" in session) and (session["is-admin"] == True):
        bird = BirdDetails.query.get_or_404(bird_id)
        bird_details = BirdDetails.query.filter_by(bird_id = bird.bird_id).first()

        if request.method == 'POST':
                b_name = request.form["name"].strip().title()
                name = b_name.replace(' ','-')
                b_scientific_name = request.form["scientific-name"].strip().title()
                scientific_name = b_scientific_name.replace(' ','-')
                description = request.form["description"]
                filename = None

                if request.files['bird-image']:
                    filename = save_bird_photo(request.files['bird-image'])
                    bird_details.image_path = filename 

                errors = validate_description_for_bird_details('description')

                if errors == {}:
                    bird_details.bird_name = name
                    bird_details.scientific_name = scientific_name
                    bird_details.description = description

                    db.session.add(bird_details)
                    db.session.commit()
                    return render_template('edit_bd.html', status="successful", errors= errors ,bird_info = bird_details)
                else:
                    return render_template('edit_bd.html', status="unsuccessful", errors= errors , bird_info = bird_details)

        elif request.method == 'GET':
            return render_template("edit_bd.html",bird_info = bird_details)
    else:
        abort(404)

@app.route("/search/Delete/<bird_id>",methods=['GET','POST'])
def delete_bird(bird_id):
    if ("username" in session) and (session["is-admin"] == True):
        bird = BirdDetails.query.get_or_404(bird_id)
        bird_details = BirdDetails.query.filter_by(bird_id = bird.bird_id).first()

        if request.method == 'POST':
            db.session.delete(bird_details)
            db.session.commit()
            return render_template('delete_bd.html', status="successful")

        elif request.method == 'GET':
            return render_template("delete_bd.html")
    else:
        abort(404)

@app.route("/bird_details_panel/",methods=['GET', 'POST'])
def bird_details_panel():
    if ("username" in session) and (session["is-admin"] == True):
        if request.method == 'POST':
            b_name = request.form["name"].strip().title()
            name = b_name.replace(' ','-')

            b_scientific_name = request.form["scientific-name"].strip().title()
            scientific_name = b_scientific_name.replace(' ','-')

            description = request.form["description"]
            filename = None

            if request.files['bird-image']:
                filename = save_bird_photo(request.files['bird-image'])

            errors = validate_description_for_bird_details('description')

            if errors == {}:
                bird_details = BirdDetails(bird_name= name, scientific_name=scientific_name, description = description, image_path=filename)
                db.session.add(bird_details)
                db.session.commit()
                return render_template('panel.html', title='Bird-details', status="successful")
            else:
                return render_template('panel.html', title='Bird-details', status="unsuccessful", errors= errors)
        
        elif request.method == 'GET':
            return render_template('panel.html', title='Bird-Details')
    else:
        abort(404)


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
            session['is-admin'] = user.is_admin
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
    session.pop('is-admin')
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
                session['is-admin'] = current_user.is_admin
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

@app.route("/superadmin_panel/", methods=['GET', 'POST'])
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
                return render_template("superadmin_panel.html", status="user-made-admin", new_admin_user = NewAdminUser, admin_users = admin_users)
            else:
                return render_template("superadmin_panel.html", status="user-does-not-exist", new_admin_user = new_admin_username, admin_users = admin_users)

        elif request.form["type"] == "revoke-rights":
            revoke_admin_username = request.form["revoke-admin-rights"]
            RevokeAdminUser = User.query.filter_by(username = revoke_admin_username).first()
            if RevokeAdminUser != None:
                RevokeAdminUser.is_admin = False
                db.session.add(RevokeAdminUser)
                db.session.commit()
                admin_users = User.query.filter_by(is_admin = True).all()
                return render_template("superadmin_panel.html", status="admin-rights-revoked", revoke_admin_user = RevokeAdminUser, admin_users = admin_users)
            else:
                return render_template("superadmin_panel.html", status="user-to-be-revoked-does-not-exist", revoke_admin_user = revoke_admin_username, admin_users = admin_users)
    
    elif request.method == "GET":
        if "username" in session:
            if session["username"] == "admin" or session["username"] == "superadmin":
                return render_template("superadmin_panel.html", admin_users = admin_users)
            else:
                abort(404)
            


# ------------------------------------ FORUM ------------------------------------
@app.route("/forum/", methods=['GET', 'POST'])
def forum():
    popular_threads = Thread.query.order_by(Thread.view_count).limit(7).all()
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
            return render_template('forum.html', title='Forum', status="unsuccessful", errors= errors, new_threads = new_threads, popular_threads=popular_threads)
    elif request.method == 'GET':
        new_threads = Thread.query.order_by(Thread.creation_date.desc()).all()
        return render_template('forum.html', title='Forum', new_threads = new_threads, popular_threads=popular_threads)

# Thread
@app.route("/forum/thread/<thread_id>", methods=['GET', 'POST'])
def thread(thread_id):
    thread = Thread.query.get_or_404(thread_id)
    replies = Reply.query.filter_by(thread_id = thread.thread_id).order_by(Reply.creation_date.desc()).all()
    thread.view_count = thread.view_count + 1
    db.session.add(thread)
    db.session.commit()
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
            is_delete_image = request.form.get("delete-image")
                
            thread = Thread.query.get(reply_id)
            errors, thread = validate_thread_for_updation(thread, thread_title, thread_caption)

            if is_delete_image:
                thread.image_path = None
            elif request.files['thread-image']:
                thread.image_path = save_thread_photo(request.files['thread-image'])

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
            is_delete_image = request.form.get("delete-image")
            filename = None
                
            reply = Reply.query.get(reply_id)
            errors, reply = validate_reply_for_updation(reply, reply_caption)

            if is_delete_image:
                reply.image_path = None
            elif request.files['reply-image']:
                reply.image_path = save_reply_photo(request.files['reply-image'])

            if errors == {}:
                db.session.add(reply)
                db.session.commit()
                replies = Reply.query.filter_by(thread_id = thread.thread_id).order_by(Reply.creation_date.desc()).all()
                return render_template('thread.html', thread = thread, replies = replies, status = 'reply-updation-successful')
            else:
                errors['reply-id'] = reply_id
                return render_template('thread.html', thread = thread, replies = replies, errors = errors, status = 'reply-updation-failed')
        elif request.form['form-type'] == 'delete-thread':
            username = session['username']
            thread_id = int(request.form["thread-id"])
            thread = Thread.query.get(thread_id)

            if thread.username == username:
                db.session.delete(thread)
                db.session.commit()
                return render_template('thread.html', thread = thread, replies = replies, status = 'thread-deletion-successful')
            else:
                return render_template('thread.html', thread = thread, replies = replies, status = 'thread-deletion-failed')
        elif request.form['form-type'] == 'delete-reply':
            username = session['username']
            reply_id = int(request.form["reply-id"])

            reply = Reply.query.get(reply_id)

            if reply.username == username:
                db.session.delete(reply)
                db.session.commit()
                replies = Reply.query.filter_by(thread_id = thread.thread_id).order_by(Reply.creation_date.desc()).all()
                return render_template('thread.html', thread = thread, replies = replies, status = 'reply-deletion-successful')
            else:
                return render_template('thread.html', thread = thread, replies = replies, status = 'reply-deletion-failed')
    elif request.method == 'GET':
        return render_template('thread.html', thread = thread, replies = replies)

@app.route("/forum/threads/", methods=['GET', 'POST'])   
def all_threads():
    pass 

# Search for a forum post
@app.route("/forum/search/", methods=['GET', 'POST'])
def thread_search():
    if request.method == "POST":
        original_query = request.form['search-query']
        query = request.form["search-query"].strip().lower()

        thread_results = Thread.query.filter(
                or_(
                func.lower(Thread.title).contains(query),
                func.lower(Thread.caption).contains(query)
            )).all()

        reply_results = Reply.query.filter(
            or_(
                func.lower(Reply.caption).contains(query)
            )).all()

        return render_template('thread_search.html', thread_results = thread_results, reply_results = reply_results, query=original_query)
    elif request.method == "GET":
        return render_template('thread_search.html')
