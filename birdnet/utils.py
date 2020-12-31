from PIL import Image
import os
from datetime import datetime
from birdnet import app
from random import randrange

def save_profile_photo(user, photo):
    file_name, file_ext = os.path.splitext(photo.filename)
    time = datetime.utcnow()
    photo_fn = str(user.user_id)  + "profile" + str(randrange(1, 20)) + str(time.timestamp()) + file_ext
    photo_path = os.path.join(app.root_path, 'static\\profile_photos', photo_fn)

    output_size = (200, 200)
    i = Image.open(photo)
    i.thumbnail(output_size)
    i.save(photo_path)

    return photo_fn

def save_thread_photo(photo):
    file_name, file_ext = os.path.splitext(photo.filename)
    time = datetime.utcnow()
    photo_fn = str(randrange(11,31)) + "thread" + str(time.timestamp()) + file_ext
    photo_path = os.path.join(app.root_path, 'static\\thread', photo_fn)

    output_size = None
    i = Image.open(photo)
    i.resize((round(i.size[0]*0.5), round(i.size[1]*0.5)))
    i.save(photo_path)

    return photo_fn

def save_reply_photo(photo):
    file_name, file_ext = os.path.splitext(photo.filename)
    time = datetime.utcnow()
    photo_fn = str(randrange(11,31)) + "reply" + str(time.timestamp()) + file_ext
    photo_path = os.path.join(app.root_path, 'static\\reply', photo_fn)

    output_size = None
    i = Image.open(photo)
    i.resize((round(i.size[0]*0.5), round(i.size[1]*0.5)))
    i.save(photo_path)

    return photo_fn