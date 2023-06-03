import sqlite3

connect = sqlite3.connect ("../../files/tables.db")
kursor = connect.cursor ()

kursor.execute ("""DROP TABLE IF EXISTS bank""")

kursor.execute ("""CREATE TABLE IF NOT EXISTS bank (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL,
    surname TEXT,
    kard_number INTEGER NOT NULL,
    name_bank INTEGER NOT NULL,
    datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)
""")

connect.commit ()