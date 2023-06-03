import sqlite3

connect = sqlite3.connect ("../../files/tables.db")
kursor = connect.cursor ()

kursor.execute ("""DROP TABLE IF EXISTS users""")

kursor.execute ("""CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    name TEXT NOT NULL,
    surname TEXT,
    phone INTEGER NOT NULL,
    password TEXT NOT NULL)
""")

connect.commit ()