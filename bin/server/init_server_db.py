import os
import sqlite3


def init_server_db():
    # Directory to create sqlite3 database file in.
    db_folder = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'db')

    # Create db folder if not already made.
    if not os.path.exists(db_folder):
        os.mkdir(db_folder)

    # Make the table.
    conn = sqlite3.connect(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                                        os.path.join('db', 'jobs.db')))
    create_table = 'CREATE TABLE IF NOT EXISTS jobs' \
                   '("id" varchar(36) NOT NULL UNIQUE,' \
                   '"status" varchar(32),' \
                   '"start_time" timestamp,' \
                   '"data" varchar(32),' \
                   'PRIMARY KEY (id))'
    conn.execute(create_table)

    conn.close()
