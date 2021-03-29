from birdnet.models import User, Thread, Reply, db
import re
from datetime import datetime

#------------FORUM-----------------------------

def validate_new_thread(title, caption):
    errors = {}

    if title == '':
            errors['title'] = 'Please enter a title for the thread'
    elif len(title) > 150:
        errors['title'] = 'Title should not be long than 150 characters'

    if caption == '':
        errors['caption'] = 'Please enter a caption'
    elif len(caption) > 400:
        errors['caption'] = 'Caption should not be long than 400 characters'

    return errors 

def validate_thread_for_updation(thread, new_title, new_caption):
    errors = {}

    if thread.title != new_title:
        if new_title == '':
            errors['new-title'] = 'Please enter a title'
        elif len(new_title) > 150:
            errors['new-title'] = 'Title should not be long than 150 characters'
        else:
            thread.title = new_title

    if thread.caption != new_caption:
        if new_caption == '':
            errors['new-caption'] = 'Please enter a caption'
        elif len(new_caption) > 400:
            errors['new-caption'] = 'Caption should not be long than 400 characters'
        else:
            thread.caption = new_caption

    return [errors, thread]

def validate_reply_for_updation(reply, new_caption):
    errors = {}

    if reply.caption != new_caption:
        if new_caption == '':
            errors['new-caption'] = 'Please enter a caption'
        elif len(new_caption) > 400:
            errors['new-caption'] = 'Caption should not be long than 400 characters'
        else:
            reply.caption = new_caption

    return [errors, reply]
 