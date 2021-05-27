from flask import Flask, flash, request, redirect, url_for, render_template, send_file
import os

PEOPLE_FOLDER = os.path.join('static','styles')
app = Flask(__name__)

@app.route("/")
def hello_world():
    return render_template('pngHome.html')

#JUST DO IT!!!
if __name__=="__main__":
    app.run(host="0.0.0.0", port="9000",threaded=False)