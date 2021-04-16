from birdnet.models import User, Thread, Reply, db
import re
from datetime import datetime

#-----------BIRD SEARCH---------------------------
def validate_bird_details(name, scientfic_name, description, image_credit):
     errors = {}

     if len(name) > 50:
          errors['name'] = 'Name should not be more than 50 characters'

     if len(scientfic_name) > 75:
          errors['scientific-name'] = 'Scientific name should not be more than 75 characters'

     if len(description) > 500:
          errors['description'] = 'Description should be less than 500 characters'
     
     if len(image_credit) > 50:
          errors['image-credit'] = 'Image credit should not be more than 100 characters'
          
     return errors