from flask import Flask, flash, request, redirect, url_for, render_template, send_file
import os
import sys
import io
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from flask_login import LoginManager, login_user, login_required, current_user, logout_user
from werkzeug.utils import secure_filename
import glob
import time
from flask_socketio import emit
import json
from datetime import datetime
import warnings
warnings.filterwarnings("ignore")

from werkzeug.security import generate_password_hash, check_password_hash
from __init__ import app, db, isAdmin, checkAdmin, socketio
from models import User

PEOPLE_FOLDER = os.path.join('static','styles')
UPLOAD_FOLDER = '../cold-extraction/csv' # Need to change this to a particular server path
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

COLD_UPLOAD_FOLDER = '../cold-extraction/' # Need to change this to a particular server path
app.config['COLD_UPLOAD_FOLDER'] = COLD_UPLOAD_FOLDER
# app = Flask(__name__)

login_manager = LoginManager(app)
login_manager.login_view = 'login'

all_jobs = {}

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

@app.route('/logs')
@login_required
def check_logs():
    return render_template('logs.html', jobs = all_jobs)

@app.route('/png-extraction')
@login_required
def png_home(name=None):
    return render_template('pngHome.html')

@socketio.on('notify-for-png')
def handle_png(png_values):
    logged_in_user = current_user.name
    if logged_in_user not in all_jobs:
        now = datetime.now()
        all_jobs[logged_in_user] = []
        all_jobs[logged_in_user].append("User " + logged_in_user + " Started PNG Extraction at: " + str(now.strftime("%d/%m/%Y, %H:%M:%S")))
    else:
        now = datetime.now()
        all_jobs[logged_in_user].append("User " + logged_in_user + " Started PNG Extraction at: " + str(now.strftime("%d/%m/%Y, %H:%M:%S")))
    logged_in_user = current_user.name
    all_logs = []
    depth = png_values['data']['depth']
    if(depth == '' or len(depth) == 0):
        depth = '0'
    chunks = png_values['data']['chunks']
    if(chunks == '' or len(chunks) == 0):
        chunks = '1'
    useProcess = png_values['data']['useProcess']
    if(useProcess == '' or len(useProcess) == 0):
        useProcess = '0'
    if not (os.path.isdir(png_values['data']['DICOMFolder'])):
        all_jobs[logged_in_user].append("User " + logged_in_user + " PNG Extraction Failed: DICOM folder does not exist")
        all_logs.append("Oops !! The Given DICOM Home Folder path is Incorrect / Does not exits / Empty")
        all_logs.append("Incorrect Execution")
        all_logs.append("Failed")
        emit('processing-finished', json.dumps({'data': all_logs}), broadcast=True)
        return
    # Checking depth is valid or not
    directory = png_values['data']['DICOMFolder'] + '/'
    i = 0
    while i < int(depth):
        directory += "*/"
        i += 1
    file_path = directory + "*.dcm"
    filelist=glob.glob(file_path, recursive=True)
    try:
        ff = filelist[0]
    except IndexError:
        all_jobs[logged_in_user].append("User " + logged_in_user + " PNG Extraction Failed: DICOM folder does not contain any DICOM files")
        all_logs.append("Given Depth is incorrect. Please provide correct depth")
        all_logs.append("Incorrect/Unsuccessful Execution")
        emit('processing-finished', json.dumps({'data': all_logs}), broadcast=True)
        return
    emit('processing', json.dumps({'loggings': 'Processing Data . . . .\n\nThis Process may take several minutes. You can check logs !!', 'pngValues': png_values}), broadcast=True)


@socketio.on('png-extraction-task')
def extract_png(png_values):
    logged_in_user = current_user.name
    config_values = {}
    config_values["DICOMHome"] = png_values['data']['data']['DICOMFolder']
    config_values["OutputDirectory"] = png_values['data']['data']['outputFolder']
    config_values["Depth"] = png_values['data']['data']['depth']
    config_values["SplitIntoChunks"] = png_values['data']['data']['chunks']
    config_values["UseProcesses"] = png_values['data']['data']['useProcess']
    config_values["FlattenedToLevel"] = png_values['data']['data']['level']
    config_values["is16Bit"] = png_values['data']['data']['is16Bit']
    config_values["PrintImages"] = png_values['data']['data']['printImages']
    config_values["CommonHeadersOnly"] = png_values['data']['data']['headers']
    config_values["SendEmail"] = png_values['data']['data']['sendEmail']
    config_values["YourEmail"] = png_values['data']['data']['email']
    if(len(config_values) > 0):
        import sys
        sys.path.append("../png-extraction/")
        import ImageExtractor
        lt = ImageExtractor.initialize_config_and_execute(config_values)
        if logged_in_user in all_jobs:
            now = datetime.now()
            all_jobs[logged_in_user].append("Finished PNG Extraction for user " + logged_in_user + " at: " + str(now.strftime("%d/%m/%Y, %H:%M:%S")))
        emit('processing-finished', json.dumps({'data': lt}), broadcast=True)

@app.route('/cold-extraction')
@login_required
def cold_extraction_home(name=None):
    csv_folder = UPLOAD_FOLDER
    if not os.path.exists(csv_folder):
        os.makedirs(csv_folder)
    files_present_in_server = os.listdir(csv_folder)
    return render_template('cold_extraction.html', files_list = files_present_in_server)

@socketio.on('processing-cold-extraction')
def loading_cold_extraction(input_json):
    logged_in_user = current_user.name
    if logged_in_user not in all_jobs:
        now = datetime.now()
        all_jobs[logged_in_user] = []
        all_jobs[logged_in_user].append("User " + logged_in_user + " Started On-demand Extraction at: " + str(now.strftime("%d/%m/%Y, %H:%M:%S")))
    else:
        now = datetime.now()
        all_jobs[logged_in_user].append("User " + logged_in_user + " Started On-demand Extraction at: " + str(now.strftime("%d/%m/%Y, %H:%M:%S")))
    logs = []
    f1 = input_json['data']['csv_file']
    if(len(f1) > 1):
        f1_name = input_json['data']['csv_file_name']
        f_path = "../cold-extraction/csv/" + f1_name
        binary_file = open(f_path, "wb")
        binary_file.write(f1)
        binary_file.close()
        input_json['data']['csv_file'] =  input_json['data']['csv_file_name']
    NifflerSystem = input_json['data']['NifflerSystem']
    NifflerSystem_File = COLD_UPLOAD_FOLDER + NifflerSystem
    checkfile = True
    try:
        with open(NifflerSystem_File, 'r') as f:
            checkfile = True
    except:
        all_jobs[logged_in_user].append("User " + logged_in_user + " Cold Extraction Failed: Niffler System File does not exist")
        err = "Error could not load given " + NifflerSystem + " file !!"
        logs.append(err)
        logs.append("UNSUCCESSFUL :( !!")
        checkfile = False
        emit('processing-finished', json.dumps({'data': logs}), broadcast=True)
        return
    
    # StorageFolder = input_json['data']['StorageFolder']
    # if (not os.path.isdir(StorageFolder)):
    #     print("Storage Folder Exists !!")
    # else:
    #     err = "Error could not find given " + StorageFolder + " folder !!"
    #     logs.append(err)
    #     logs.append("UNSUCCESSFUL :( !!")
    #     checkfile = False
    #     emit('processing-finished', json.dumps({'data': logs}), broadcast=True)
    #     return

    emit('processing', json.dumps({'data': 'Processing Data . . . .\n\nThis Process may take several minutes or Hours. You can check logs !!', 'cold_Values': input_json}), broadcast=True)

@socketio.on('running-cold-extraction')
@login_required
def cold_extraction(cold_values):
    logged_in_user = current_user.name
    logs = []
    cold_extraction_values = {}

    f1 = cold_values['data']['data']['csv_file_name']
    f2 = cold_values['data']['data']['csv_file_path']
    if(f1):
        cold_extraction_values['CsvFile'] = os.path.join(app.config['UPLOAD_FOLDER'],f1)
    else:
        cold_extraction_values['CsvFile'] = os.path.join(app.config['UPLOAD_FOLDER'],f2)
        
    NifflerSystem = cold_values['data']['data']['NifflerSystem']
    if(NifflerSystem == '' or len(NifflerSystem) == 0):
        NifflerSystem = 'system.json'
    file_path = cold_values['data']['data']['FilePath']
    if(file_path == '' or len(file_path) == 0):
        file_path = '{00100020}/{0020000D}/{0020000E}/{00080018}.dcm'
    date_format = cold_values['data']['data']['DateFormat']
    if(date_format == '' or len(date_format) == 0):
        date_format = '%Y%m%d'
    cold_extraction_values['NifflerSystem'] = NifflerSystem
    cold_extraction_values['StorageFolder'] = cold_values['data']['data']['StorageFolder']
    cold_extraction_values['FilePath'] = file_path
    cold_extraction_values['FirstAttr'] = cold_values['data']['data']['FirstAttr']
    cold_extraction_values['FirstIndex'] = cold_values['data']['data']['FirstIndex']
    cold_extraction_values['SecondAttr'] = cold_values['data']['data']['SecondAttr']
    cold_extraction_values['SecondIndex'] = cold_values['data']['data']['SecondIndex']
    cold_extraction_values['ThirdAttr'] = cold_values['data']['data']['ThirdAttr']
    cold_extraction_values['ThirdIndex'] = cold_values['data']['data']['ThirdIndex']
    cold_extraction_values['NumberOfQueryAttributes'] = cold_values['data']['data']['NumberOfQueryAttributes']
    cold_extraction_values['DateFormat'] = date_format
    cold_extraction_values['SendEmail'] = cold_values['data']['data']['SendEmail']
    cold_extraction_values['YourEmail'] = cold_values['data']['data']['YourEmail']
    import sys
    import io
    sys.path.append(COLD_UPLOAD_FOLDER)
    import ColdDataRetriever
    os.chdir(COLD_UPLOAD_FOLDER)
    import ColdDataRetriever
    x = ColdDataRetriever.initialize_config_and_execute(cold_extraction_values)
    logs.append("No errors encountered")
    logs.append("Cold Extraction is SUCCESSFUL !!")
    if logged_in_user in all_jobs:
        now = datetime.now()
        all_jobs[logged_in_user].append("Finished On-Demand Extraction for user " + logged_in_user + " at: " + str(now.strftime("%d/%m/%Y, %H:%M:%S")))
    emit('processing-finished', json.dumps({'data': logs}), broadcast=True)

#JUST DO IT!!!
if __name__=="__main__":
    # app.run(host="0.0.0.0",port="9000")
    socketio.run(app,host="0.0.0.0")
