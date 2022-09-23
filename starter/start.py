from subprocess import Popen
import os
Popen(["gunicorn", "-k", "eventlet", "-w", "3", "app:app", "-b", "0.0.0.0:"+os.environ.get("PORT")],shell=True,bufsize=1)