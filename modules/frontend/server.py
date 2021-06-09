from flask import Flask, flash, request, redirect, url_for, render_template, send_file
import os

PEOPLE_FOLDER = os.path.join('static','styles')
app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
    return render_template('home.html')

@app.route("/png-extraction", methods = ['GET'])
def PNG_Extraction():
    return render_template('pngHome.html')

config_values = {}

@app.route('/', methods=['POST'])
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

#JUST DO IT!!!
if __name__=="__main__":
    app.run(port="9000")