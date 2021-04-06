from PIL import Image
import os
from datetime import datetime
from birdnet import app
from random import randrange
import numpy as np

from tensorflow.keras.preprocessing.image import img_to_array

class_dict = {
    0:"ALEXANDRINE PARAKEET",
    1:"ANNAS HUMMINGBIRD",
    2:"ANTBIRD",
    3:"BALD EAGLE",
    4:"BARN OWL",
    5:"BARN SWALLOW",
    6:"BELTED KINGFISHER",
    7:"BLACK SWAN",
    8:"BLACK VULTURE",
    9:"BLACK-THROATED SPARROW",
    10:"CHIPPING SPARROW",
    11:"CROW",
    12:"CROWNED PIGEON",
    13:"DOWNY WOODPECKER",
    14:"EMPEROR PENGUIN",
    15:"EMU",
    16:"FLAMINGO",
    17:"GILA WOODPECKER",
    18:"HORNBILL",
    19:"HOUSE SPARROW",
    20:"JAVA SPARROW",
    21:"KING VULTURE",
    22:"KIWI",
    23:"LONG-EARED OWL",
    24:"MALABAR HORNBILL",
    25:"MALACHITE KINGFISHER",
    26:"MALLARD DUCK",
    27:"MANDRIN DUCK",
    28:"MYNA",
    29:"NICOBAR PIGEON",
    30:"OSTRICH",
    31:"PEACOCK",
    32:"PELICAN",
    33:"ROCK DOVE",
    34:"RUFOUS KINGFISHER",
    35:"SNOWY OWL",
    36:"STORK BILLED KINGFISHER",
    37:"TREE SWALLOW",
    38:"TRUMPTER SWAN",
    39:"WOOD DUCK"
}
 
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
    processed_dict = {}
    processed_list = []

    p = predictions[0]

    for n in range(0,40):
        if round(p[n], 5) > 0:
            predicted_index = n
            a = round((p[n]*100), 2)
            processed_dict[a] = (class_dict[predicted_index]).capitalize()

    for key, value in processed_dict.items():
        processed_list.append([key, value])

    processed_list.sort(reverse = True)
    processed_list = processed_list[0:5]

    return processed_list
    