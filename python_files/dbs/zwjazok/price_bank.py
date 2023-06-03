import sqlite3

connect = sqlite3.connect ("../../../files/tables.db")
kursor = connect.cursor ()

kursor.execute ("""DROP TABLE IF EXISTS price_bank""")

kursor.execute ("""CREATE TABLE IF NOT EXISTS price_bank (
    id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    id_price INTEGER NOT NULL,
    id_bank INTEGER NOT NULL,
    FOREIGN KEY (id_price) REFERENCES price(id),
    FOREIGN KEY (id_bank) REFERENCES bank(id)
)""")