# importing in modules 
import os
import shutil
import plotly
from flask import Flask, request, render_template, redirect, url_for
from flask import send_from_directory, Response, send_file
from flask import session, request, copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect
from flask_session import Session
from werkzeug.utils import secure_filename
import sys
from datetime import datetime
from time import sleep
import subprocess
from uuid import uuid4
import csv
import json
import random
from transitions import Machine, State

# Setting State (Still learning)
class Webstate(object):
    def curerntlyactive(self): print("currently active")
    def curentlyidle(self): print("currently idle!")

webcheck = Webstate()
webtransitions = [
    {'trigger':'webactive','source':'idle','dest':'active'},
    {'trigger':'webidle','source':'active','dest':'idle'},
]
machine = Machine(model=webcheck, states=[{
                                            'name':'idle',
                                            'on_exit':['curerntlyactive']}, 
                                            {'name':'active',
                                            'on_exit':['curentlyidle']}], initial='idle',
                                            transitions=webtransitions)


# Setting Variables
app = Flask(__name__,static_folder="static/",template_folder="templates/")
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
socketio = SocketIO(app,logger=False, engineio_logger=False)
Session(app)
app.secret_key = "secret key"
ALLOWED_EXTENSIONS = set(['csv'])
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
path = os.getcwd()

# Parsing the filename and returning data back
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Home route that acts different based on if its a Get or Post request
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            webcheck.webactive()
            UPLOAD_FOLDER = os.path.join(path, 'upload',session['number'])
            if not os.path.isdir(UPLOAD_FOLDER):
                os.makedirs(UPLOAD_FOLDER)
            filename = secure_filename(file.filename)
            save_location = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_location)
            socketio.emit('uploadcomplete')
            webcheck.webidle()
    else:
        session['number'] = str(uuid4())
    return render_template('index.html', async_mode=socketio.async_mode), 200

# A route for the forecast template
@app.route('/forecast', methods=['GET', 'POST'])
def forecast(figs):
    graphJSON = []
    for fig in figs:
        graphJSON.append(json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder))
    return render_template('forecast.html', graphJSON=graphJSON)

# A Websocket to remove that tmp and upload folder after the prediction is finished.
@socketio.event
def killdata():
    shutil.rmtree('./static/tmp/'+str(session['number']))
    shutil.rmtree('./upload/'+str(session['number']))

# The websocket that starts the run.py prediction model
@socketio.event
def run_forecast():
    webcheck.webactive()
    config_fn = './src/config.yaml'

    # Creating the upload folder
    UPLOAD_FOLDER = os.path.join(path, 'upload',session['number'])

    # Checking to make sure the upload folder exists
    if not os.path.isdir(UPLOAD_FOLDER):
        emit('logerror',{"errormessage":"File Missing","loginfo": "No file is selected. Please select a file using the 'Browse'."+ "<br>"})
        uploadfoldercheck = "failed"
        fp_211_check = "failed"
    else:
        uploadfoldercheck = "success"

    # Checking to make sure the fp_211 variable can be created without issue
    if uploadfoldercheck == "success":
        try:
            fp_211 = os.path.join(UPLOAD_FOLDER, os.listdir(UPLOAD_FOLDER)[0])
            fp_211_check = "success"
        except IndexError:
            emit('logerror',{"errormessage":"File Missing","loginfo": "No file is selected. Please select a file using the 'Browse'."+ "<br>"})
            fp_211_check = "failed"

    if fp_211_check == "success":
        # Creating temporary folder location for the prediction model process
        tempfolderlocation = './static/tmp/'+str(session['number'])
        if not os.path.isdir(tempfolderlocation):
            os.makedirs(tempfolderlocation)
        try:
            os.environ["PYTHONUNBUFFERED"] = "1"
            emit('clearoutput')
            # starting realtime pipe to websocket
            with subprocess.Popen(["python","run.py","--211",fp_211,"--config_yaml",config_fn,"--tempsource",tempfolderlocation],stdout=subprocess.PIPE,shell=False,bufsize=1,universal_newlines=True) as process:
                for linestdout in process.stdout:
                    linestdout = linestdout.rstrip()
                    try:
                        emit('logForcast',{"loginfo": linestdout+ "<br>"})
                        print(linestdout)
                    except Exception as e:
                        exception_type, exception_object, exception_traceback = sys.exc_info()
                        filename = exception_traceback.tb_frame.f_code.co_filename
                        line_number = exception_traceback.tb_lineno
                        exceptstring = str(exception_type).replace("<","").replace(">","")
                        reason = "ERROR: "+ str(exception_object)+"<br>\
                        Exception type: "+ str(exceptstring)+"<br>\
                        File name: "+ str(filename)+"<br>\
                        Line number: "+ str(line_number)+"<br>"
                        emit('logForcast',{"loginfo": str(reason)+ "<br>"})
                        print(str(reason))
                        webcheck.webidle()

            # getting the csv data and sending it to the client browser
            csvlistdata = []
            with open('./static/tmp/'+str(session['number']+"/model_scoring/predictions.csv"), encoding='utf-8') as csvf:
                    csvReader = csv.DictReader(csvf)
                    for rows in csvReader:
                        csvlistdata.append(rows)
            emit('showcsv',{"showcsvinfo": csvlistdata})

            # getting the chart picture data and sending it to the client browser
            forecast_fn = os.path.join('static','tmp', str(session['number']), 'create_viz',
                                'forecast.png')
            with open(forecast_fn, 'rb') as f:
                image_data = f.read()
            emit('forcastphoto',{"loginfo": image_data})
            webcheck.webidle()
            # Unfortionately, I don't think subprocess popen can pull a return value like this to get
            # The attribute of figs... You may need to think about how to pipe
            # Your variables to the app since Popen is only used to run commands. 
            # You could try the subprocess.check_output() command but you wont get the realtime results, only the return value 
            # subprocess.Popen or subprocess.run can
            # THIS WONT WORK - redirect(url_for('forecast'), figs=process.figs)
            # You probably want something like this (Look at option 2 in line 206
            # of run.py file):
            # forecast_vars = os.path.join('static','tmp', str(session['number']), 'create_viz',
            #                     ''figs.json')
            # with open(forecast_vars, 'rb') as f:
            #     forecast_data = f.read()
            # redirect(url_for('forecast'), figs=forecast_data)
        except Exception as e:
            exception_type, exception_object, exception_traceback = sys.exc_info()
            filename = exception_traceback.tb_frame.f_code.co_filename
            line_number = exception_traceback.tb_lineno
            exceptstring = str(exception_type).replace("<","").replace(">","")
            reason = "ERROR: "+ str(exception_object)+"<br>\
            Exception type: "+ str(exceptstring)+"<br>\
            File name: "+ str(filename)+"<br>\
            Line number: "+ str(line_number)+"<br>"

            emit('logForcast',{"loginfo": str(reason)+ "<br>"})
            webcheck.webidle()




# A disconnection socket, may or may not be used
@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == "__main__":
    # app.run(host="127.0.0.1", port=5000, threaded=True)
    # socketio.run(app,host="127.0.0.1", port=5000, threaded=True)
    # app.run(host="0.0.0.0", port=5000, threaded=True)
    # socketio.run(app,host="0.0.0.0", port=5000, threaded=True)
    app.run(host="0.0.0.0", port=os.environ.get("PORT"), threaded=True)
    socketio.run(app,host="0.0.0.0", port=os.environ.get("PORT"), threaded=True)
