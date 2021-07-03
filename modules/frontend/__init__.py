from flask import Flask, render_template, flash
import os
import sys
from functools import wraps
from flask_sqlalchemy import SQLAlchemy
import warnings
warnings.filterwarnings("ignore")

PEOPLE_FOLDER = os.path.join('static','styles')
app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret-key-goes-here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db = SQLAlchemy(app)

isAdmin = False
if(len(sys.argv) > 1 and sys.argv[1] == '--admin'):
    isAdmin = True
else:
    isAdmin = False

def checkAdmin(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        isAdmin = False
        if(len(sys.argv) > 1 and sys.argv[1] == '--admin'):
            isAdmin = True
        else:
            isAdmin = False
        if(isAdmin == False):
            flash("Sorry, You do not have permission to access this page\nPlease contact admin")
            return render_template('login.html')
        return func(*args, **kwargs)
    return decorated_function