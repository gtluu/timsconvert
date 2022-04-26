import os
import sqlite3


conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    os.path.join('db', 'jobs.db')))

create_table = 'CREATE TABLE IF NOT EXISTS jobs (id varchar(36) NOT NULL UNIQUE, status varchar(32), PRIMARY KEY (id))'

conn.execute(create_table)

conn.close()
