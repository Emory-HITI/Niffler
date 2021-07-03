from flask import Flask, flash, request, redirect, url_for, render_template, send_file
import os
import sys
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.utils import secure_filename
import warnings
warnings.filterwarnings("ignore")

from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import app, db, isAdmin, checkAdmin
from models import User

PEOPLE_FOLDER = os.path.join('static','styles')
UPLOAD_FOLDER = '../cold-extraction/csv' # Need to change this to a particular server path
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

COLD_UPLOAD_FOLDER = '../cold-extraction/' # Need to change this to a particular server path
app.config['COLD_UPLOAD_FOLDER'] = COLD_UPLOAD_FOLDER
# app = Flask(__name__)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    # since the user_id is just the primary key of our user table, use it in the query for the user
    return User.query.get(int(user_id))

@app.route("/", methods=['GET'])
def index():
    return render_template('Home.html', isAdmin = isAdmin)

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
        return render_template('Home.html')
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
    return render_template('Home.html', isAdmin = isAdmin)

@app.route('/png-extraction', methods=['GET', 'POST'])
@login_required
def extract_png():
    config_values = {}
    if request.method =='POST':
        depth = request.form['depth']
        if(depth == '' or len(depth) == 0):
            depth = '0'
        chunks = request.form['chunks']
        if(chunks == '' or len(chunks) == 0):
            chunks = '1'
        useProcess = request.form['useProcess']
        if(useProcess == '' or len(useProcess) == 0):
            useProcess = '0'

        config_values["DICOMHome"] = request.form['DICOMFolder']
        config_values["OutputDirectory"] = request.form['outputFolder']
        config_values["Depth"] = request.form['depth']
        config_values["SplitIntoChunks"] = request.form['chunks']
        config_values["UseProcesses"] = request.form['useProcess']
        config_values["FlattenedToLevel"] = request.form['level']
        config_values["is16Bit"] = request.form['16Bit']
        config_values["PrintImages"] = request.form['printImages']
        config_values["CommonHeadersOnly"] = request.form['headers']
        config_values["SendEmail"] = request.form['sendEmail']
        config_values["YourEmail"] = request.form['email']
        if(len(config_values) > 0):
            import sys
            sys.path.append("../png-extraction/")
            import ImageExtractor
            lt = ImageExtractor.initialize_config_and_execute(config_values)
            return render_template('pngHome.html', logs = lt)
    return render_template('pngHome.html')

@app.route('/cold-extraction', methods=['GET', 'POST'])
@login_required
def cold_extraction():
    logs = []
    csv_folder = UPLOAD_FOLDER
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)
    files_present_in_server = os.listdir(csv_folder)

    cold_extraction_values = {}
    if request.method =='POST':
        f1 = request.files['csvFile_choose']
        f2 = request.form['csvFile_name']
        if(f1):
            filename = secure_filename(f1.filename)
            f1.save(os.path.join(app.config['UPLOAD_FOLDER'],filename))
            cold_extraction_values['CsvFile'] = os.path.join(app.config['UPLOAD_FOLDER'],filename)
        else:
            cold_extraction_values['CsvFile'] = os.path.join(app.config['UPLOAD_FOLDER'],f2)
            
        NifflerSystem = request.form['NifflerSystem']
        if(NifflerSystem == '' or len(NifflerSystem) == 0):
            NifflerSystem = 'system.json'
        file_path = request.form['file_path']
        if(file_path == '' or len(file_path) == 0):
            file_path = '{00100020}/{0020000D}/{0020000E}/{00080018}.dcm'
        accession_index = request.form['AccessionIndex']
        if(accession_index == '' or len(accession_index) == 0):
            accession_index = '1'
        patient_index = request.form['PatientIndex']
        if(patient_index == '' or len(patient_index) == 0):
            patient_index = '0'
        date_index = request.form['DateIndex']
        if(date_index == '' or len(date_index) == 0):
            date_index = '1'
        date_format = request.form['DateFormat']
        if(date_format == '' or len(date_format) == 0):
            date_format = '%Y%m%d'

        NifflerSystem_File = COLD_UPLOAD_FOLDER + NifflerSystem
        checkfile = True
        try:
            with open(NifflerSystem_File, 'r') as f:
                checkfile = True
        except:
            err = "Error could not load given " + NifflerSystem + " file !!"
            logs.append(err)
            checkfile = False

        if checkfile:
            cold_extraction_values['NifflerSystem'] = NifflerSystem_File
            cold_extraction_values['storage_folder'] = request.form['StorageFolder']
            cold_extraction_values['file_path'] = file_path
            cold_extraction_values['extraction_type'] = request.form['ExtractionType']
            cold_extraction_values['accession_index'] = accession_index
            cold_extraction_values['patient_index'] = patient_index
            cold_extraction_values['date_index'] = date_index
            cold_extraction_values['date_type'] = request.form['DateType']
            cold_extraction_values['date_format'] = date_format
            cold_extraction_values['send_email'] = request.form['sendEmail']
            cold_extraction_values['email'] = request.form['email']

            import sys
            import io
            sys.path.append("../cold-extraction/")
            import ColdDataRetriever
            x = ColdDataRetriever.initialize_config_and_execute(cold_extraction_values)
            return render_template('cold_extraction.html', logs = logs, files_list = files_present_in_server)
        else:
            return render_template('cold_extraction.html', logs = logs, files_list = files_present_in_server)
    return render_template('cold_extraction.html', files_list = files_present_in_server)
#JUST DO IT!!!
if __name__=="__main__":
    app.run(host="0.0.0.0",port="9000")
