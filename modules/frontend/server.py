from flask import Flask, flash, request, redirect, url_for, render_template, send_file
import os
import sys
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
import warnings
warnings.filterwarnings("ignore")

from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import app, db, isAdmin, checkAdmin
from models import User

PEOPLE_FOLDER = os.path.join('static','styles')
# app = Flask(__name__)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

@app.route("/", methods=['GET'])
def index():
    return render_template('home.html', isAdmin = isAdmin)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')
        remember = True if request.form.get('remember') else False

        user = User.query.filter_by(email=email).first()

        # check if the user actually exists
        # take the user-supplied password, hash it, and compare it to the hashed password in the database
        if not user or not check_password_hash(user.password, password):
            flash('Please check your login details and try again.')
            return render_template('login.html') # if the user doesn't exist or password is wrong, reload the page

        # if the above check passes, then we know the user has the right credentials
        login_user(user, remember=remember)
        return render_template('home.html')
    return render_template('login.html', isAdmin = isAdmin)

@app.route('/signup', methods=['GET','POST'])
@checkAdmin
def signup():
    if request.method =='POST':
        email = request.form.get('email')
        name = request.form.get('name')
        password = request.form.get('password')

        user = User.query.filter_by(email=email).first() # if this returns a user, then the email already exists in database

        if user: # if a user is found, we want to redirect back to signup page so user can try again
            flash('Email address already exists')
            return render_template('signup.html')

        # create a new user with the form data. Hash the password so the plaintext version isn't saved.
        new_user = User(email=email, name=name, password=generate_password_hash(password, method='sha256'))

        # add the new user to the database
        db.session.add(new_user)
        db.session.commit()
        return render_template('login.html', isAdmin = isAdmin)

    return render_template('signup.html', isAdmin = isAdmin)

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return render_template('home.html', isAdmin = isAdmin)

# @app.route("/png-extraction", methods = ['GET'])
# @login_required
# def PNG_Extraction():
#     return render_template('pngHome.html')

config_values = {}

@app.route('/png-extraction', methods=['GET', 'POST'])
@login_required
def extract_png():
    if request.method =='POST':
        config_values["dcmFolder"] = request.form['DICOMFolder']
        config_values["outputFolder"] = request.form['outputFolder']
        config_values["depth"] = request.form['depth']
        config_values["chunks"] = request.form['chunks']
        config_values["useProcess"] = request.form['useProcess']
        config_values["level"] = request.form['level']
        config_values["16Bit"] = request.form['16Bit']
        config_values["printImages"] = request.form['printImages']
        config_values["headers"] = request.form['headers']
        config_values["sendEmail"] = request.form['sendEmail']
        config_values["email"] = request.form['email']

        if(len(config_values) > 0):
            import sys
            sys.path.append("../png-extraction/")
            import ImageExtractor
            lt = ImageExtractor.initialize_Values(config_values)
            return render_template('pngHome.html', logs = lt)
    return render_template('pngHome.html')

@app.route('/cold-extraction', methods=['GET', 'POST'])
@login_required
def cold_extraction():
    if request.method =='POST':
        csv_file = request.files['csvFile']
        if (csv_file):
            import sys
            import io

            stream = io.StringIO(csv_file.stream.read().decode("UTF8"), newline=None)
            sys.path.append("../cold-extraction/")
            import ColdDataRetriever
            x = ColdDataRetriever.read_csv(stream)
    return render_template('cold_extraction.html')
#JUST DO IT!!!
if __name__=="__main__":
    app.run(port="9000")