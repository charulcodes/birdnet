from flask import Blueprint
from flask import render_template, session, request, redirect, url_for, flash, abort
from datetime import datetime
from sqlalchemy import or_, func
from PIL import Image
import os, io, base64

from tensorflow.keras.applications.mobilenet import preprocess_input

from birdnet.models import User, Thread, Reply, BirdDetails, db
from birdnet import app, bcrypt, birdid_model
from birdnet.main.validations import validate_bird_details
from birdnet.main.utils import save_bird_photo, preprocess_image, process_predictions

main = Blueprint('main', __name__)

# ------------------------------------ HOME & ABOUT PAGES ------------------------------------
@main.route("/")
def index():
    random_bird = BirdDetails.query.order_by(func.random()).first()
    return render_template('main/index.html', bird = random_bird)

@main.route("/about/")
def about():
    return render_template('main/about.html')

# ------------------------------------ TOOLS ------------------------------------
@main.route("/birdid/", methods=['GET', 'POST'])
def birdid():
    if request.method == "POST":
        image = None
        if request.files['bird-image']:
            image = request.files['bird-image']
        
        opened_image = Image.open(image)
        processed_image = preprocess_image(opened_image, target_size=(224, 224))
        processed_image = preprocess_input(processed_image)
        
        output = io.BytesIO()
        opened_image.save(output, format='JPEG')
        output.seek(0)
        output_s = output.read()
        b64 = base64.b64encode(output_s).decode('ascii')

        predictions = birdid_model.predict(processed_image).tolist()
        prediction_dict = process_predictions(predictions)
        return render_template('main/birdid.html', title='Bird Identification', predictions = prediction_dict, is_image_posted = True, imgString=b64)
    elif request.method == "GET":
        return render_template('main/birdid.html', title='Bird Identification')

@main.route("/search/", methods=['GET','POST'])
def search():
    if request.method == 'POST':
       bird = request.form['search-query'].strip().title()
       bird = bird.replace(' ','-')
       
       if bird != "":
           results = BirdDetails.query.filter(
               or_(
                   BirdDetails.bird_name.contains(bird),
                   BirdDetails.scientific_name.contains(bird)
                   )).all()
       else:
           results = None

       return render_template('main/search.html', bird_data = results)
    elif request.method == 'GET':
       return render_template('main/search.html')

@main.route("/search/Edit/<bird_id>",methods=['GET','POST'])
def edit_bird(bird_id):
    if ("username" in session) and (session["is-admin"] == True):
        bird = BirdDetails.query.get_or_404(bird_id)
        bird_details = BirdDetails.query.filter_by(bird_id = bird.bird_id).first()

        if request.method == 'POST':
                b_name = request.form["name"].strip().title()
                name = b_name.replace(' ','-')
                b_scientific_name = request.form["scientific-name"].strip().title()
                scientific_name = b_scientific_name.replace(' ','-')
                image_credit = request.form["image-credit"]
                description = request.form["description"]
                filename = None

                if request.files['bird-image']:
                    filename = save_bird_photo(request.files['bird-image'])
                    bird_details.image_path = filename 

                errors = validate_bird_details(name, scientific_name, description, image_credit)

                if errors == {}:
                    bird_details.bird_name = name
                    bird_details.scientific_name = scientific_name
                    bird_details.image_credit = image_credit
                    bird_details.description = description

                    db.session.add(bird_details)
                    db.session.commit()
                    flash("Data updated successfully")
                    return redirect(url_for('main.edit_bird', bird_id = bird.bird_id))
                else:
                    return render_template('main/edit_bd.html', status="unsuccessful", errors= errors, bird_info = bird_details)

        elif request.method == 'GET':
            return render_template("main/edit_bd.html", bird_info = bird_details)
    else:
        abort(404)

@main.route("/search/Delete/<bird_id>",methods=['GET','POST'])
def delete_bird(bird_id):
    if ("username" in session) and (session["is-admin"] == True):
        bird = BirdDetails.query.get_or_404(bird_id)
        bird_details = BirdDetails.query.filter_by(bird_id = bird.bird_id).first()

        if request.method == 'POST':
            db.session.delete(bird_details)
            db.session.commit()
            flash("Bird entry for \"" + bird.bird_name +  "\" deleted successfully")
            return redirect(url_for('main.bird_details_panel'))

        elif request.method == 'GET':
            return render_template("main/delete_bd.html")
    else:
        abort(404)

@main.route("/bird_details_panel/",methods=['GET', 'POST'])
def bird_details_panel():
    if ("username" in session) and (session["is-admin"] == True):
        if request.method == 'POST':
            b_name = request.form["name"].strip().title()
            name = b_name.replace(' ','-')
            b_scientific_name = request.form["scientific-name"].strip().title()
            scientific_name = b_scientific_name.replace(' ','-')

            image_credit = request.form["image-credit"]
            description = request.form["description"]
            filename = None

            if request.files['bird-image']:
                filename = save_bird_photo(request.files['bird-image'])

            errors = validate_bird_details(name, scientific_name, description, image_credit)

            if errors == {}:
                bird_details = BirdDetails(bird_name= name, scientific_name=scientific_name, description = description, image_credit = image_credit, image_path=filename)
                db.session.add(bird_details)
                db.session.commit()
                flash("Data saved successfully")
                return redirect(url_for('main.bird_details_panel'))
            else:
                return render_template('main/panel.html', title='Bird-details', status="unsuccessful", errors= errors)
        
        elif request.method == 'GET':
            return render_template('main/panel.html', title='Bird-Details')
    else:
        abort(404)

# ------------------------------------ ERROR PAGES ------------------------------------
@main.errorhandler(404)
def page_not_found(error):
    return render_template('main/page_not_found.html'), 404
