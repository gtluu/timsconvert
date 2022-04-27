import os
from server.apps import app
from server.constants import JOBS_DB
from server.init_server_db import *


if __name__ == '__main__':
    if not os.path.exists(JOBS_DB):
        init_server_db()
    app.run(port=5000,
            threaded=True,
            processes=1)
