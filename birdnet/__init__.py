from flask import Flask, session
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_migrate import Migrate

from tensorflow.keras.models import Sequential, load_model
import os

app = Flask(__name__, 
        static_url_path='', 
        static_folder='static',
        template_folder='templates')

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:root@localhost/birdnet'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

birdid_model = load_model(os.path.join(os.getcwd(), 'birdnet', '12_birds_model_v4'))

app.config['SECRET_KEY'] = 'bird_secret'
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db

app_session = Session(app)

bcrypt = Bcrypt(app)

# DO NOT move this import to top
from birdnet import routes 