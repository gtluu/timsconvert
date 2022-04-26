import os
import sqlite3


db_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db')

if not os.path.exists(db_folder):
    os.mkdir(db_folder)

conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                    os.path.join('db', 'jobs.db')))

create_table = 'CREATE TABLE IF NOT EXISTS jobs ("id" varchar(36) NOT NULL UNIQUE, "status" varchar(32), PRIMARY KEY (id))'

conn.execute(create_table)

conn.close()
