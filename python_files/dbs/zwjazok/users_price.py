import sqlite3

connect = sqlite3.connect ("../../../files/tables.db")
kursor = connect.cursor ()

kursor.execute ("""DROP TABLE IF EXISTS users_price""")

kursor.execute ("""CREATE TABLE IF NOT EXISTS users_price (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    id_users INTEGER NOT NULL,
    id_price INTEGER NOT NULL,
    FOREIGN KEY (id_users) REFERENCES users(id),
    FOREIGN KEY (id_price) REFERENCES price(id)
)""")