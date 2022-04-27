from flask import Flask
from flask_executor import Executor
from server.constants import *


# Make Flask instance.
app = Flask(__name__)

# Create and set upload folder.
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Set max file size.
app.config['MAX_CONTENT_PATH'] = 1000000000

# Make Executor instance.
executor = Executor(app)
# Set executor to only use one thread.
app.config['EXECUTOR_MAX_WORKERS'] = 1
