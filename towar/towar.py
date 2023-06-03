import flask
import sqlite3
from werkzeug.exceptions import abort

def return_connect ():
    connect = sqlite3.connect ("files/tables.db")
    connect.row_factory = sqlite3.Row
    return connect

towarapp = flask.Blueprint ("towar", __name__,
    template_folder = "templates",
    static_folder = "static"
)

@towarapp.route("/add")
def add ():
    try:
        if flask.session.get ("islogin"):
            connect = return_connect ()
            kursor = connect.cursor ()
            kursor.execute ("""SELECT name, surname FROM users
            WHERE id == (?)""", [flask.session.get ("id")])
            data = kursor.fetchone ()

            kursor.execute ("""SELECT MAX(id) FROM price""")

            auto_id = kursor.fetchone ()[0]
            auto_id = int(str(auto_id).replace ("None", "0"))
            auto_id += 1

            return flask.render_template ("add.html", data = data, auto_id = auto_id)
        else:
            abort (404)
    except KeyError:
        abort (404)

def endadd ():
    try:
        if flask.request.method == "POST" and flask.session.get ("islogin"):
            connect = sqlite3.connect ("files/tables.db")
            kursor = connect.cursor ()

            name_towar = flask.request.form.get ("name_towar")
            writing = flask.request.form.get ("writing")
            id_ = flask.request.form.get ("id")
            amount = flask.request.form.get ("amount")

            #Це дані про товар

            name = flask.request.form.get ("name")
            surname = flask.request.form.get ("surname")
            kard_number = flask.request.form.get ("kard_number")
            name_bank = flask.request.form.get ("name_bank")
            price = flask.request.form.get ("price")
            currency = flask.request.form.get ("currency")
            category = flask.request.form.get ("category")

            #Це банківські, для переказу грошей, дані

            writing = writing.replace ("<", "(")
            writing = writing.replace (">", ")")

            #Редагування опису

            kursor.execute ("""SELECT * FROM price
                WHERE id == (?)
            """, [id_])
            check = kursor.fetchone ()
            if check is None:
                kursor.execute ("""INSERT INTO price (
                    id, name, writing, amount, price, currency, category)
                    VALUES (?, ?, ?, ?, ?, ?, ?)""",
                    [id_, name_towar, writing, amount, price, currency, category])
                    
                
                kursor.execute ("""INSERT INTO bank (
                    name, surname, kard_number, name_bank)
                    VALUES (?, ?, ?, ?)""",
                    [name, surname, kard_number, name_bank])
                
                kursor.execute ("""INSERT INTO users_price (
                    id_price, id_users)
                    VALUES (?, ?)""",
                    [id_, flask.session.get ("id")])
                
                kursor.execute ("""SELECT id FROM bank ORDER BY datetime DESC""")
                id_bank = kursor.fetchone ()[0]

                kursor.execute ("""INSERT INTO price_bank (
                    id_bank, id_price)
                    VALUES (?, ?)
                """, [id_bank, id_])

                connect.commit ()
            
            else:
                flask.flash ("Такий ідентифікаційний ключ вже є, придумайте інший!🤔🤔🤔")

            return flask.redirect (flask.url_for ("home.main"))
        else:
            abort (404)
    except KeyError:
        abort (404)

def edit (id_):
    try:
        if flask.session.get ("islogin"):
            connect = return_connect ()
            kursor = connect.cursor ()

            kursor.execute ("""SELECT id_users FROM users_price
            WHERE id_price == (?)""", [id_])
            u_id = kursor.fetchone ()

            if int(flask.session.get ("id")) == u_id["id_users"]:

                kursor.execute ("""SELECT name, writing, amount, id, currency, price, category FROM price
                WHERE id == (?)""", [id_])
                data = kursor.fetchone ()

                writing = data["writing"].replace ("&lt", "<")
                writing = writing.replace ("&gt", ">")

                kursor.execute ("""SELECT bank.name, bank.surname, bank.kard_number, bank.name_bank FROM bank
                JOIN price_bank ON bank.id = price_bank.id_bank
                JOIN price ON price.id = price_bank.id_price
                WHERE price.id == (?)""", [id_])
                bank = kursor.fetchone ()

                return flask.render_template ("edit.html", data = data, bank = bank, writing=writing)
            else:
                flask.flash ("Ви не продаєте цей товар!")
                return flask.redirect (flask.url_for ("home.main"))
        else:
            abort (404)
    except KeyError:
        abort (404)
towarapp.add_url_rule ("/edit/id_=<int:id_>", "edit", edit)

@towarapp.route("/endedit/id_=<int:id_>", methods = ["POST", "GET"])
def endedit (id_):
    try:
        if flask.request.method == "POST" and flask.session.get ("islogin"):
            connect = sqlite3.connect ("files/tables.db")
            kursor = connect.cursor ()

            name_towar = flask.request.form.get ("name_towar")
            writing = flask.request.form.get ("writing")
            u_id = flask.request.form.get ("id")
            amount = flask.request.form.get ("amount")

            #Це дані про товар

            name = flask.request.form.get ("name")
            surname = flask.request.form.get ("surname")
            kard_number = flask.request.form.get ("kard_number")
            name_bank = flask.request.form.get ("name_bank")
            price = flask.request.form.get ("price")
            currency = flask.request.form.get ("currency")
            category = flask.request.form.get ("category")

            #Це банківські, для переказу грошей, дані

            writing = writing.replace ("<", "&lt")
            writing = writing.replace (">", "&gt")

            #Редагування опису
            kursor.execute ("""UPDATE bank
            SET name = (?),
            surname = (?),
            kard_number = (?),
            name_bank = (?)
            WHERE id IN (
                SELECT price_bank.id_bank
                FROM price_bank
                INNER JOIN price ON price.id = price_bank.id_price
                WHERE price.id = (?))""",
            [name, surname, kard_number, name_bank, id_])
                
            kursor.execute ("""UPDATE users_price
                SET id_price = (?)
                WHERE id_price == (?)
                """, [u_id, id_])

            kursor.execute ("""UPDATE price_bank
                SET id_price = (?)
                WHERE id_price == (?)
                """, [u_id, id_])
            
            kursor.execute ("""UPDATE price 
                SET id = (?),
                name = (?),
                writing = (?),
                amount = (?),
                price = (?),
                currency = (?),
                category = (?)
                WHERE id == (?)""",
                [u_id, name_towar, writing, amount, price, currency, category, id_])

            connect.commit ()

        return flask.redirect (flask.url_for ("home.main"))
    except KeyError:
        abort (404)
    except sqlite3.IntegrityError:
        flask.flash ("Такий ідентифікаційний ключ вже є, придумайте інший!🤔🤔🤔")
        return flask.redirect (flask.url_for ("home.main"))

def delete ():
    try:
        if flask.session.get ("islogin"):
            id_ = flask.request.args.get ("id")
            connect = sqlite3.connect ("files/tables.db")
            kursor = connect.cursor ()

            kursor.execute ("""SELECT id_users FROM users_price
            WHERE id_price == (?)
            """, [id_])
            u_id = kursor.fetchone ()[0]
            if int (flask.session.get ("id")) == u_id:
                kursor.execute ("""SELECT bank.id FROM bank
                JOIN price_bank ON bank.id = price_bank.id_bank
                JOIN price ON price.id = price_bank.id_price
                WHERE price.id == (?)""", [id_])
                b_id = kursor.fetchone ()[0]

                kursor.execute ("""DELETE FROM price_bank
                WHERE id_price == (?)""", [id_])

                kursor.execute ("""DELETE FROM bank
                WHERE id == (?)""", [b_id])

                kursor.execute ("""DELETE FROM users_price
                WHERE id_price == (?)""", [id_])

                kursor.execute ("""DELETE FROM price
                WHERE id == (?)""", [id_])

                connect.commit ()

            else:
                flask.flash ("Ви не продаєте цей товар!")

            return flask.redirect (flask.url_for ("home.main"))

        else:
            abort (404)
    except KeyError:
        abort (404)
towarapp.add_url_rule ("/deleteprice", "delete", delete)


towarapp.add_url_rule ("/endadd", "endadd", endadd, methods = ["POST", "GET"])