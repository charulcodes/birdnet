from birdnet.models import User, Thread, Reply, db
import re
from datetime import datetime

#-----------BIRD SEARCH---------------------------

def validate_description_for_bird_details(description):
   errors = {}
   if len(description) > 500:
        errors['description'] = 'Description should be less than 500 characters'
   
   return errors