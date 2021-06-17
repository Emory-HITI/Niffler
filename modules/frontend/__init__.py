from flask import Flask
import os
from flask_sqlalchemy import SQLAlchemy
import warnings
warnings.filterwarnings("ignore")

PEOPLE_FOLDER = os.path.join('static','styles')
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)