import sqlite3

conn = sqlite3.connect('bullflix.db')

conn.execute('CREATE TABLE users (USER_GUID integer primary key, USER_NAME TEXT, EMAIL TEXT, PIP_HASH TEXT)')

conn.close()
