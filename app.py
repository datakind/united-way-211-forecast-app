import os
import shutil
import yaml
from flask import Flask, request, render_template, redirect, url_for
from flask import send_from_directory, Response, send_file, session, request, copy_current_request_context
from flask_socketio import SocketIO, emit, disconnect
from flask_session import Session
from werkzeug.utils import secure_filename
from datetime import datetime
from time import sleep
import subprocess
from uuid import uuid4
import csv

# from run import run_script
from src.run import run

app = Flask(__name__,static_folder="static/",template_folder="templates/")
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
socketio = SocketIO(app,logger=False, engineio_logger=False)
Session(app)

app.secret_key = "secret key"

ALLOWED_EXTENSIONS = set(['csv'])
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
path = os.getcwd()
# file Upload
UPLOAD_FOLDER = os.path.join(path, 'uploads')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            # logger.info(file.filename)
            filename = secure_filename(file.filename)
            save_location = os.path.join(UPLOAD_FOLDER, filename)
            file.save(save_location)
            print(save_location)
    else:
        session['number'] = str(uuid4())
    return render_template('index.html', async_mode=socketio.async_mode), 200

@socketio.event
def killdata():
    shutil.rmtree('./static/tmp/'+str(session['number']))
    

@socketio.event
def run_forecast():
    config_fn = './src/config.yaml'
    # fp_211 = os.listdir(UPLOAD_FOLDER)
    fp_211 = './data/211/raw/'
    tempfolderlocation = './static/tmp/'+str(session['number'])

    with open(config_fn, 'r') as fn:
        config = yaml.safe_load(fn)

    config['preprocessing_config']['data_fp'] = fp_211
    try:
        os.environ["PYTHONUNBUFFERED"] = "1"
        with subprocess.Popen(["python","run.py","--211",fp_211,"--config_yaml",config_fn,"--tempsource",tempfolderlocation],stdout=subprocess.PIPE,shell=False,bufsize=1,universal_newlines=True) as process:
            for linestdout in process.stdout:
                linestdout = linestdout.rstrip()
                try:
                    emit('logForcast',{"loginfo": linestdout+ "<br>"})
                    print(linestdout)
                except Exception as e:
                    emit('logForcast',{"loginfo": str(e)+ "<br>"})
                    print(str(e))

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
    except Exception as e:
        emit('logForcast',{"loginfo": str(e)+ "<br>"})

# A disconnection socket, may or may not be used
@socketio.on('disconnect')
def test_disconnect():
    print('Client disconnected', request.sid)

if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, threaded=True)
    socketio.run(app,host="127.0.0.1", port=5000, threaded=True)
