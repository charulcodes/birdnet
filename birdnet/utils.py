from PIL import Image
import os
from datetime import datetime
from birdnet import app

def save_profile_photo(user, photo):
    file_name, file_ext = os.path.splitext(photo.filename)
    time = datetime.utcnow()
    photo_fn = str(user.user_id) + "profile" + str(time.timestamp()) + file_ext
    photo_path = os.path.join(app.root_path, 'static\\profile_photos', photo_fn)

    output_size = (200, 200)
    i = Image.open(photo)
    i.thumbnail(output_size)
    i.save(photo_path)

    return photo_fn