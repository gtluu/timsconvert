from flask import Flask
from redis import Redis
from rq import Queue
from constants import *


# Make Flask instance.
app = Flask(__name__)

# Create and set upload folder.
if not os.path.exists(UPLOAD_FOLDER):
    os.mkdir(UPLOAD_FOLDER)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# Set max file size.
app.config['MAX_CONTENT_PATH'] = 1000000000

# Queue configuration.
q = Queue(connection=Redis())
