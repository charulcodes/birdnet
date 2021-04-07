from flask import Flask, session
from flask_bcrypt import Bcrypt
from flask_sqlalchemy import SQLAlchemy
from flask_session import Session
from flask_migrate import Migrate

from tensorflow.keras.models import load_model
import os

app = Flask(__name__, 
        static_url_path='', 
        static_folder='static',
        template_folder='templates')

db_username = os.environ.get('PG_DB_USER')
db_psec = os.environ.get('PG_DB_PSEC')
bsk = os.environ.get('BIRD_BSK')

app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://' + db_username + ':' + db_psec + '@localhost/birdnet'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

birdid_model = load_model(os.path.join(os.getcwd(), 'birdnet', 'birdnetv6_MobileNet'))

app.config['SECRET_KEY'] = bsk
app.config['SESSION_TYPE'] = 'sqlalchemy'
app.config['SESSION_SQLALCHEMY'] = db

app_session = Session(app)

bcrypt = Bcrypt(app)

# DO NOT move this import to top
from birdnet.forum.routes import forum
from birdnet.users.routes import users
from birdnet.main.routes import main

app.register_blueprint(forum)
app.register_blueprint(users)
app.register_blueprint(main)