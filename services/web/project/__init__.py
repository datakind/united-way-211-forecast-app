import os

from werkzeug.utils import secure_filename
from flask import (
    Flask,
    request,
    render_template,
    Response,
    send_from_directory,
    redirect,
    url_for
)
from flask_cors import CORS
from datetime import datetime
from .run import run_script
from time import sleep
from loguru import logger

app = Flask(__name__)
app.config.from_object("project.config.Config")
# print(app.config["output_fp"])
CORS(app)

ALLOWED_EXTENSIONS = set(['csv'])
path = os.getcwd()
UPLOAD_FOLDER = os.path.join(path, 'uploads')

if not os.path.isdir(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route("/")
def index():
    if request.method == 'POST':
        file = request.files['file']
        if file and allowed_file(file.filename):
            logger.info(file.filename)
            filename = secure_filename(file.filename)
            save_location = os.path.join(app.config["UPLOAD_FOLDER"], filename)
            file.save(save_location)

    return render_template('index.html'), 200


@app.route('/run_model', methods=['GET', 'POST'])
def run_model():
    files = os.listdir(UPLOAD_FOLDER)
    run_script(files, UPLOAD_FOLDER, app)

    return send_from_directory('run/model_scoring/', 'predictions.csv')


@app.route("/static/<path:filename>")
def staticfiles(filename):
    return send_from_directory(app.config["STATIC_FOLDER"], filename)


@app.route("/media/<path:filename>")
def mediafiles(filename):
    return send_from_directory(app.config["MEDIA_FOLDER"], filename)


@app.route("/upload", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        file = request.files["file"]
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config["MEDIA_FOLDER"], filename))
    return """
    <!doctype html>
    <title>upload new File</title>
    <form action="" method=post enctype=multipart/form-data>
      <p><input type=file name=file><input type=submit value=Upload>
    </form>
    """


@app.route('/download')
def download():
    return render_template('download.html', files=os.listdir('run/model_scoring'))


@app.route('/download/<filename>')
def download_file(filename):
    return send_from_directory('run/model_scoring', filename)


# adjusted flask_logger
def flask_logger():
    """creates logging information"""
    open("run/job.log", 'w').close()
    with open("run/job.log") as log_info:
        for i in range(1000000):
            data = log_info.read()
            yield data.encode()
            sleep(1)


@app.route("/stream", methods=["GET", "POST"])
def stream():
    """returns logging information"""
    return Response(flask_logger(), mimetype="text/plain", content_type="text/event-stream")
