from flask import Flask, flash, request, redirect, url_for, render_template, send_file
import os

PEOPLE_FOLDER = os.path.join('static','styles')
app = Flask(__name__)

@app.route("/", methods=['GET'])
def index():
    return render_template('home.html')


@app.route('/png-extraction', methods=['POST', 'GET'])
def extract_png():
    config_values = {}
    if request.method =='POST':
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

#JUST DO IT!!!
if __name__=="__main__":
    app.run(port="9000")