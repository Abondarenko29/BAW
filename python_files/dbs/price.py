import sqlite3

connect = sqlite3.connect ("../../files/tables.db")
kursor = connect.cursor ()

kursor.execute ("DROP TABLE IF EXISTS price")

kursor.execute ("""CREATE TABLE IF NOT EXISTS price (
    id INTEGER PRIMARY KEY NOT NULL,
    name VARCHAR (140) NOT NULL,
    writing TEXT,
    currency TEXT NOT NULL,
    price REAL NOT NULL,
    amount INTEGER NOT NULL,
    category VARCHAR (140),
    datetime TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP)
""")

connect.commit ()