import flask
import sqlite3
from werkzeug.exceptions import abort
import vonage
import python_files.config as config

def return_connect ():
    connect = sqlite3.connect ("files/tables.db")
    connect.row_factory = sqlite3.Row
    return connect






def return_client (): #Тут не треба розбиратися, ця функція створює клієнта для надсилання смс та не впливає на роботу бази даних.
    client = vonage.Client (key = config.key, secret = config.secret)
    sms = vonage.Sms (client)
    return sms

def send_sms (client, text, from_, to): #Тут не треба розбиратися, ця функція надсилає sms.
    responseData = client.send_message(
    {
        "from": from_,
        "to": f"+{to}",
        "text": text,
    }
    )
    if responseData["messages"][0]["status"] == "0":
        return True
    else:
        return f"Щось пішло не так: {responseData['messages'][0]['error-text']}"







buyapp = flask.Blueprint ("buy", __name__,
    template_folder = "templates",
    static_folder = "static"
)



def buy (id_):
    try:
        if flask.session.get ("islogin"):
            connect = return_connect ()
            kursor = connect.cursor ()

            kursor.execute ("""SELECT amount FROM price
            WHERE id == (?)""", [id_])
            amount = kursor.fetchone ()

            if amount["amount"] > 0:

                kursor.execute ("""SELECT price.currency, price.price
                    FROM users
                JOIN users_price ON users_price.id_price = price.id
                JOIN price ON price.id = users_price.id_price
                WHERE price.id == (?)""", [id_])
                data = kursor.fetchone ()

                kursor.execute ("""SELECT name, surname FROM users
                WHERE id == (?)""", [flask.session.get ("id")])
                data2 = kursor.fetchone ()

                return flask.render_template ("buy.html", data = data, id = id_, data2 = data2, amount = amount)
            else:
                flask.flash ("Товару немає у наявності❗❗❗")
                return flask.redirect (flask.url_for ("home.main"))
        else:
            abort (404)
    except KeyError:
        abort (404)
buyapp.add_url_rule ("/buy/<int:id_>", "buy", buy, methods = ["GET", "POST"])

@buyapp.route ("/endbuy", methods = ["GET", "POST"])
def endbuy():
    try:
        if flask.request.method == "POST" and flask.session.get ("islogin"):
            id_ = flask.request.args.get ("id")
            connect = sqlite3.connect ("files/tables.db")
            kursor = connect.cursor ()
            kursor.execute ("""SELECT users.phone FROM users, users_price, price
            WHERE price.id == (?)""", [id_])
            data = kursor.fetchone ()
            phone = data[0]

            kursor.execute ("""SELECT phone FROM users
            WHERE id == (?)""", [flask.session.get ("id")])
            phone_from = data[0]

            kursor.execute ("""SELECT currency, price, name FROM price
            WHERE id == (?)""", [id_])
            data = kursor.fetchone ()

            currency, price, towar_name = data

            client = return_client ()
            sucsess = send_sms (client,
                                text = f"+{phone_from} buy some. His article {id_}.",
                                from_ = "BAW",
                                to = phone)
            print (phone)
            
            if sucsess:

                kursor.execute ("""SELECT bank.name, bank.surname, bank.kard_number, bank.name_bank FROM bank, price, price_bank
                WHERE price.id == (?)""", [id_])
                data = kursor.fetchone ()
                name_seller, surname_seller, kard_number_seller, name_bank_seller = data

                name_buyer = flask.request.form.get ("name")
                surname_buyer = flask.request.form.get ("surname")
                bank_name_buyer = flask.request.form.get ("bank_name")
                kard_number_buyer = flask.request.form.get ("kard_number")

                amount_buyed = int(flask.request.form.get ("amount"))

                cdata = {"₴":"UAH",
                        "$":"USD",
                        "€":"EUR",
                        "₿":"BTC",
                        "zł":"PLN"}
                
                currency = cdata[currency]

                print (f"""Адресант: {name_seller} {surname_seller}, Його номер картки: {kard_number_seller}, Його назва банку: {name_bank_seller}.\n
                Адресат: {name_buyer}, {surname_buyer}, Його номер картки: {kard_number_buyer}, Його назва банку: {bank_name_buyer}.\n
                Ось ще важливі дані:\n\nВалюта: {currency},\nСума переказу: {price * amount_buyed}""")

                kursor.execute ("""SELECT amount FROM price
                WHERE id == (?)""", [id_])
                amount = kursor.fetchone ()[0]

                kursor.execute ("""UPDATE price
                SET amount == (?)
                WHERE id == (?)""", [amount - amount_buyed, id_])

                connect.commit ()

                return flask.redirect (flask.url_for ("home.main"))
            else:
                flask.flash (sucsess)
                flask.redirect (flask.url_for ("home.main"))
        else:
            abort (404)
    except KeyError:
        abort (404)


@buyapp.route ("/buyed/<int:id_>")
def buyed (id_):
    try:
        if flask.session.get ("islogin"):
            connect = sqlite3.connect ("files/tables.db")
            kursor = connect.cursor ()

            kursor.execute ("""SELECT id_users FROM users_price
            WHERE id_price == (?)
            """, [id_])
            u_id = kursor.fetchone ()[0]

            if int (flask.session.get ("id") == u_id):

                kursor.execute ("""SELECT amount FROM price
                WHERE id == (?)""", [id_])
                amount = kursor.fetchone ()[0]

                if amount > 0:
                    kursor.execute ("""UPDATE price
                    SET amount = (?)
                    WHERE id == (?)""", [amount - 1, id_])

                    connect.commit ()
                
                else:
                    flask.flash ("Такого товару немає, його не можна купити!")
            
            else:
                flask.flash ("Ви не продаєте цей товар!")

            return flask.redirect (flask.url_for ("home.main"))
        else:
            abort (404)
    except KeyError:
        abort (404)