from flask import Flask
from flask_executor import Executor
from timsconvert_server.constants import *


app = Flask(__name__, template_folder=TEMPLATES_DIR)

if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_PATH'] = 1000000000

executor = Executor(app)
