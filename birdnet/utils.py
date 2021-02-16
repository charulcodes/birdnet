from PIL import Image
import os
from datetime import datetime
from birdnet import app
from random import randrange
import numpy as np

from tensorflow.keras.preprocessing.image import ImageDataGenerator, img_to_array

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

def save_bird_photo(photo):
    file_name, file_ext = os.path.splitext(photo.filename)
    time = datetime.utcnow()
    photo_fn = str(randrange(11,31)) + "birdsearch" + str(time.timestamp()) + file_ext
    photo_path = os.path.join(app.root_path, 'static\\birdsearch_collection', photo_fn)

    output_size = None
    i = Image.open(photo)
    i.resize((round(i.size[0]*0.5), round(i.size[1]*0.5)))
    i.save(photo_path)

    return photo_fn

def preprocess_image(image, target_size):
    if image.mode != "RGB":
        image = image.convert("RGB")
    image = image.resize(target_size)
    image = img_to_array(image)
    image = np.expand_dims(image, axis=0)
    return image

def process_predictions(predictions):
    class_dict = {
    0:"ANNAS HUMMINGBIRD",
    1:"ANTBIRD",
    2:"BALD EAGLE",
    3:"BARN OWL",
    4:"BARN SWALLOW",
    5:"BELTED KINGFISHER",
    6:"BLACK SWAN",
    7:"DOWNY WOODPECKER",
    8:"EMPEROR PENGUIN",
    9:"OSTRICH",
    10:"PEACOCK",
    11:"TRUMPTER SWAN"
    }

    processed_dict = {}
    processed_list = []

    p = predictions[0]

    for n in range(0,12):
        if round(p[n], 5) > 0:
            predicted_index = n
            a = round((p[n]*100), 3)
            processed_dict[a] = (class_dict[predicted_index]).capitalize()

    for key, value in processed_dict.items():
        processed_list.append([key, value])

    processed_list.sort(reverse = True)

    return processed_list
    
