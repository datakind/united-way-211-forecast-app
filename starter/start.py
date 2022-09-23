import subprocess
import os
subprocess.Popen(["gunicorn", "-k", "eventlet", "-w", "3", "app:app", "-b", "0.0.0.0:"+os.environ.get("PORT")],stdout=subprocess.PIPE,shell=True,bufsize=1)