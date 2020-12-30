from birdnet import app, db
from datetime import datetime

class User(db.Model):
    user_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    username = db.Column(db.String(50), unique=True, nullable=False) 
    email = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(65), nullable=False)
    firstname = db.Column(db.String(50), nullable=False)
    lastname = db.Column(db.String(50), nullable=False)
    gender = db.Column(db.String(1), nullable=False)
    profile_photo_path = db.Column(db.String(200), default="default.png")
    bio = db.Column(db.String(300))
    signup_date = db.Column(db.DateTime, default=datetime.utcnow)

    threads = db.relationship('Thread', backref="creator", lazy=True)

    def __repr__():
        return f"User('{self.username}','{self.email}','{self.signup_date}')"

class Thread(db.Model):
    thread_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    username = db.Column(db.String(50), db.ForeignKey('user.username'), nullable=False)
    title = db.Column(db.String(150), nullable=False)
    caption = db.Column(db.String(400), nullable=False)
    image_path = db.Column(db.String(200))
    view_count = db.Column(db.Integer)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)

    replies = db.relationship('Reply', backref="parent_thread", lazy=True)

    def __repr__():
        return f"Username: ('{self.username}', Title: '{self.title}', Date posted: '{self.post_date}')"

class Reply(db.Model):
    reply_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    username = db.Column(db.String(50), db.ForeignKey('user.username'), nullable=False)
    caption = db.Column(db.String(400), nullable=False)
    image_path = db.Column(db.String(200))
    thread_id = db.Column(db.Integer, db.ForeignKey('thread.thread_id'), nullable=False)
    creation_date = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__():
        return f"Username: ('{self.username}', Date replied: '{self.post_date}')"

class BirdDetails(db.Model):
    bird_id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    bird_name = db.Column(db.String(50), nullable=False)
    scientific_name = db.Column(db.String(75), nullable=False)
    image_path = db.Column(db.String(200))
    description = db.Column(db.String(300), nullable=False)
