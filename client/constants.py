import os


URL = 'http://localhost:5000'  # change to GNPS URL later
LOCAL_JOBS_DB = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
                             'db',
                             'local_jobs.db')
