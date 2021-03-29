from flask import Blueprint
from flask import render_template, session, request, redirect, url_for, abort
from datetime import datetime
from sqlalchemy import or_, func
from PIL import Image
import os, io, base64

from birdnet.models import User, Thread, Reply, BirdDetails, db
from birdnet import app, bcrypt, birdid_model
from birdnet.forum.validations import validate_new_thread, validate_thread_for_updation, validate_reply_for_updation
from birdnet.forum.utils import  save_thread_photo, save_reply_photo

forum = Blueprint('forum', __name__)

# ------------------------------------ FORUM ------------------------------------
@forum.route("/forum/", methods=['GET', 'POST'])
def forum_main():
    popular_threads = Thread.query.order_by(Thread.view_count.desc()).limit(7).all()
    new_threads = Thread.query.order_by(Thread.creation_date.desc()).limit(5).all()
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
            new_threads = Thread.query.order_by(Thread.creation_date.desc()).limit(5).all()
            return render_template('forum.html', title='Forum', status="successful", new_threads = new_threads)
        else:
            return render_template('forum.html', title='Forum', status="unsuccessful", errors= errors, new_threads = new_threads, popular_threads=popular_threads)
    elif request.method == 'GET':
        return render_template('forum.html', title='Forum', new_threads = new_threads, popular_threads=popular_threads)

# Thread
@forum.route("/forum/thread/<thread_id>", methods=['GET', 'POST'])
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
                
            thread = Thread.query.get(thread_id)
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

@forum.route("/forum/threads/", methods=['GET'])   
def all_threads():
    page = request.args.get('page', 1, type=int)
    threads = Thread.query.order_by(Thread.creation_date.desc()).paginate(per_page=5)
    return render_template('all_threads.html', threads = threads)

# Search for a forum post
@forum.route("/forum/search/", methods=['GET', 'POST'])
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
