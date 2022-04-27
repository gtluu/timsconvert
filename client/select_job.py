import logging
import sqlite3
import pandas as pd
from client.constants import LOCAL_JOBS_DB


def select_job():
    with sqlite3.connect(LOCAL_JOBS_DB) as conn:
        query = 'SELECT * FROM jobs'
        jobs_table = pd.read_sql_query(query, conn)
    id_list = jobs_table['id'].values.tolist()
    for i, id in enumerate(id_list, start=1):
        logging.info(str(id) + '. ' + str(id))
    entry = input('Select a job ID (Enter a number): ')
    job_uuid = id_list[int(entry) - 1]
    return job_uuid
