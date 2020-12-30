from birdnet.models import User, db
import re
from datetime import datetime

def validate_new_user(firstname, lastname, gender, email, username, password, reconfirmed_password):
    email_regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
    pwd_regex = reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,50}$"
    errors = {}

    if firstname == "":
        errors["firstname"] =  "Please enter your first name"
    elif len(firstname) > 50:
        errors["firstname"] = "First name should be less than 50 characters"

    if lastname == "":
        errors["lastname"] = "Please enter your last name"
    elif len(lastname) > 50:
        errors["lastname"] = "Last name should be less than 50 characters"

    if gender == "":
        errors["gender"] = "Please select your gender"

    if email == "":
        errors["email"] = "Please enter your email"
    elif re.search(email_regex, email) == None:
        error["email"] = "Invalid email, please enter a valid email"
    elif len(email) >= 254:
        errors["email"] = "Email too long"

    if username == "":
        errors["username"] = "Please enter your username"
    elif len(username) > 50:
        errors["username"] = "Username should be less than 50 characters"
    
    if password != reconfirmed_password:
        errors["password"] = "Entered passwords do not match"
    elif re.search(pwd_regex, password) == None:
        errors["password"] = "pwd_error_message"

    user = User.query.filter_by(username = username).first()
    user_email = User.query.filter_by(email = email).first()

    if user:
        errors["username"] = "Username is already taken. Please use another username."
        
    if user_email:
        errors["email"] = "Email-id is already taken. Please use another email-id"

    return errors

def validate_details_for_updation(current_user, firstname, lastname, gender, email, username, bio):
    email_regex = "^[a-z0-9]+[\._]?[a-z0-9]+[@]\w+[.]\w{2,3}$"
    errors = {}

    if current_user.firstname != firstname:
            if firstname == "":
                errors["firstname"] =  "Please enter your first name"
            elif len(firstname) > 50:
                errors["firstname"] = "First name should be less than 50 characters"
            else:
                current_user.firstname = firstname

    if current_user.lastname != lastname:
        if lastname == "":
            errors["lastname"] = "Please enter your last name"
        elif len(lastname) > 50:
            errors["lastname"] = "Last name should be less than 50 characters"
        else:
            current_user.lastname = lastname

    if current_user.gender != gender:
        if gender == "":
            errors["gender"] = "Please select your gender"
        else:
            current_user.gender = gender

    if current_user.bio != bio:
        if len(bio) > 300:
            errors["bio"] = "About section can be upto 300 characters only."
        elif bio == "":
            current_user.bio = None
        else:
            current_user.bio = bio

    if current_user.email != email:
        user_email = User.query.filter_by(email = request.form['email']).first()
        if email == "":
            errors["email"] = "Please enter your email"
        elif re.search(email_regex, email) == None:
            error["email"] = "Invalid email, please enter a valid email"
        elif len(email) >= 254:
            errors["email"] = "Email too long"
        elif user_email:
            errors["email"] = "Email-id is already taken. Please use another email-id" 
        else:
            current_user.email = email          

    if current_user.username != username:
        user = User.query.filter_by(username = username).first()
        if username == "":
            errors["username"] = "Please enter your username"
        elif len(username) > 50:
            errors["username"] = "Username should be less than 50 characters"
        elif user:
            errors["username"] = "Username is already taken. Please use another username."
        else:
            current_user.username = username

    return [errors, current_user]

def validate_password(password, reconfirmed_password):
    pwd_regex = reg = "^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*#?&])[A-Za-z\d@$!#%*?&]{6,50}$"

    if re.search(pwd_regex, password) == None:
        return False
    else:
        return True       

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
