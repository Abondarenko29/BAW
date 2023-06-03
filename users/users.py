import flask
import sqlite3
import phonenumbers
from werkzeug.exceptions import abort
from twilio.rest import Client
import python_files.config as config
from twilio.base.exceptions import TwilioRestException
import requests.exceptions as con

account_sid = config.account_sid
auth_token = config.auth_token

client = Client(account_sid, auth_token)

def to_str (list_) -> str:
    str_ = ""
    for element in list_:
        str_ += str(element) + f", "
    str_ = str_[:-1]
    return str_

def return_client ():
    global client
    return client

def return_text (list_element):
    list_element = list_element[0]
    return list_element

def send_smscode (number, client):
    verify_sid = config.verify_sid
    verified_number = f"+{str(number)}"
    verification = client.verify.v2.services(verify_sid) \
    .verifications \
    .create(to=verified_number, channel="sms")

def check_code (code, number, client):
    number = f"+{str(number)}"
    verification_check = client.verify.v2.services(config.verify_sid) \
    .verification_checks \
    .create(to=number, code=code)

    if verification_check.status == "approved":
        return True
    elif verification_check.status == "pending":
        return False


def return_connect ():
    connect = sqlite3.connect ("files/tables.db")
    connect.row_factory = sqlite3.Row
    return connect

usersapp = flask.Blueprint ("users", __name__,
    template_folder = "templates",
    static_folder = "static"
)

@usersapp.route ("/up")
def register ():
    try:
        del flask.session["data"]
        return flask.redirect (flask.url_for("users.register"))
    except:
        return flask.render_template ("register.html")

@usersapp.route ("/isdelete")
def isdelete ():
    return flask.render_template ("delete.html")

def delete ():
    try:
        if flask.session.get ("islogin"):
            connect = sqlite3.connect ("files/tables.db")
            kursor = connect.cursor ()





            kursor.execute ("""SELECT id_price FROM users_price
            WHERE id_users == (?)""", [flask.session.get ("id")])
            data = kursor.fetchall ()
            price_ids = tuple (map(return_text, data))
            #price_ids = to_str (price_ids)

            print (price_ids)

            kursor.execute ("""SELECT bank.id FROM bank
            JOIN price_bank ON bank.id = price_bank.id_bank
            JOIN price ON price.id = price_bank.id_price
            WHERE price.id IN (
                SELECT id_price FROM users_price
            WHERE id_users == (?))""", [flask.session.get ("id")])
            data = kursor.fetchall ()
            bank_ids = tuple(map(return_text, data))
            #bank_ids = to_str (bank_ids)

            kursor.execute ("""DELETE FROM users_price
            WHERE id_users = (?)""", [flask.session.get ("id")])

            for price_id in price_ids:
                print (price_id)

                kursor.execute ("""DELETE FROM price_bank
                WHERE id_price = (?)""", (price_id, ))

                kursor.execute ("""DELETE FROM price
                WHERE id = (?)""", (price_id, ))

            for bank_id in bank_ids:
                print (bank_id)

                kursor.execute ("""DELETE FROM bank
                WHERE id = (?)""", (bank_id, ))

            kursor.execute ("""DELETE FROM users
            WHERE id = (?)""", [flask.session.get ("id")])

            connect.commit ()

            return flask.redirect (flask.url_for ("login.logout"))
        else:
            flask.redirect (flask.url_for ("login.logout"))
    except KeyError:
        abort (404)
usersapp.add_url_rule ("/delete_account", "delete", delete)

def check_phone ():
    if flask.request.method == "POST":
        connect = sqlite3.connect ("files/tables.db")
        kursor = connect.cursor ()
        name = flask.request.form.get ("name")
        surname = flask.request.form.get ("surname")
        phone = flask.request.form.get ("phone")
        password = flask.request.form.get ("password")
        repeat = flask.request.form.get ("repeat")
        kursor.execute ("""SELECT id FROM users WHERE phone == (?)""", [phone])
        check = kursor.fetchone ()
        flask.session ["data"] = [name, surname, phone, password]
        try:
            number_check = phonenumbers.parse(phone, "GB")
            phone = int(phone[1:])
            if phonenumbers.is_valid_number(number_check):
                if repeat == password:
                    if check is None:
                        try:
                            client = return_client ()
                            send_smscode (phone, client)
                        except con.ConnectionError:
                            flask.flash ("Проблеми з під'єднанням до інтернету!")
                            return flask.redirect (flask.url_for ("users.register"))
                        except TwilioRestException:
                            flask.flash ("Ви забагато разів просили надсилати код перевірки, зачекайте 10 хвилин!")
                        return flask.render_template ("check_your_number.html")
                    else:
                        flask.flash ("На цей номер зареєстрований обліпковий запис!")
                else:
                    flask.flash ("Пароль повторено непрваильно!")
            else:
                flask.flash ("Такого номеру не існує!")
        except phonenumbers.NumberParseException:
            flask.flash ("Такого номеру не існує!")
        return flask.render_template ("register.html")
    else:
        return abort (404)
usersapp.add_url_rule ("/up/check", "check_your_phone", check_phone, methods = ["GET", "POST"])

def edit ():
    try:
        if flask.session.get ("islogin"):
            connect = sqlite3.connect ("files/tables.db")
            connect.row_factory = sqlite3.Row
            kursor = connect.cursor ()
            kursor.execute ("""SELECT * FROM users
            WHERE id = (?)
            """, [flask.session.get ("id")])
            data = kursor.fetchone ()
            return flask.render_template ("edit.html", data = data)
        else:
            abort (404)
    except KeyError:
        abort (404)
usersapp.add_url_rule ("/edit", "edit", edit, methods = ["GET", "POST"])

@usersapp.route ("/endedit", methods = ["GET", "POST"])
def endedit ():
    try:
        if flask.request.method == "POST" and flask.session.get ("islogin"):
            connect = sqlite3.connect ("files/tables.db")
            kursor = connect.cursor ()
            name = flask.request.form.get ("name")
            surname = flask.request.form.get ("surname")
            phone = flask.request.form.get ("phone")
            kursor.execute ("""SELECT id FROM users WHERE phone == (?)""", [phone])
            check = kursor.fetchone ()

            if check[0] == int(flask.session.get ("id")):
                check = None

            flask.session ["new_data"] = [name, surname, phone]
            try:
                number_check = phonenumbers.parse(phone, "GB")
                phone = int(phone[1:])
                if phonenumbers.is_valid_number(number_check):
                    if check is None:
                        try:
                            client = return_client ()
                            send_smscode (phone, client)
                        except con.ConnectionError:
                            flask.flash ("Проблеми з під'єднанням до інтернету!")
                            return flask.redirect (flask.url_for ("users.edit"))
                        # except TwilioRestException:
                        #     flask.flash ("Ви забагато разів просили надсилати код перевірки, зачекайте 10 хвилин!")
                        return flask.render_template ("check_your_number.html")
                    else:
                        flask.flash ("На цей номер зареєстрований обліпковий запис!")
                else:
                    flask.flash ("Такого номеру не існує!")
            except phonenumbers.NumberParseException:
                flask.flash ("Такого номеру не існує!")
            return flask.redirect (flask.url_for ("users.edit"))
        else:
            return abort (404)
    except KeyError:
        abort (404)

def new_data ():
    try:
        name, surname, phone = flask.session.get ("data")
        if flask.request.method == "POST" and flask.session.get ("islogin"):
            connect = sqlite3.connect ("files/tables.db")
            kursor = connect.cursor ()

            check = flask.session.get ("check")
            client = return_client ()
            ischeck = check_code (check, phone, client)

            if ischeck:
                kursor.execute ("""UPDATE users
                SET name = (?),
                surname = (?),
                phone = (?)
                WHERE id = (?)""", [name, surname, phone, flask.session.get ("id")])

                connect.commit ()

                kursor.execute ("""SELECT * FROM users
                WHERE id == (?)
                """, [flask.session.get ("id")])

                data = kursor.fetchone ()

                del flask.session["data"]
                flask.session["islogin"] = True
                flask.session["id"] = data["id"]

                return flask.render_template ("data.html", data=data)

            elif ischeck == False:
                flask.flash ("Код введено неправильно!")
                return flask.redirect (flask.url_for ("users.edit"))

            else:
                flask.flash ("Сталася помилка!")
                return flask.redirect (flask.url_for ("users.edit"))
    except KeyError:
        abort (404)

usersapp.add_url_rule ("/data/new", "new_data", new_data, methods = ["GET", "POST"])

def update_password ():
    try:
        if flask.session.get ("islogin"):
            return flask.render_template ("update_password.html")

        else:
            abort (404)

    except KeyError:
        abort (404)

usersapp.add_url_rule ("/update_password", "update_password", update_password, methods = ["GET", "POST"])



@usersapp.route ("/endupdate_pasword", methods = ["GET", "POST"])
def endupdate_pasword ():
    try:
        if flask.session.get ("islogin") and flask.request.method == "POST":
            connect = sqlite3.connect ("files/tables.db")
            kursor = connect.cursor ()

            kursor.execute ("""SELECT password FROM users
            WHERE id = (?)""", [flask.session.get ("id")])

            original_before_password = kursor.fetchone ()[0]

            #Отримання даних із форми
            before_password = flask.request.form.get ("before_password")
            password = flask.request.form.get ("password")
            repeat = flask.request.form.get ("repeat")
            #========================

            first_if = not (original_before_password == before_password)

            second_if = not (password == repeat)

            if first_if:
                flask.flash ("Старий пароль введено неправильно!🤔🤔🤔")

            if second_if:
                flask.flash ("Ви не так повторили новий пароль!🤔🤔🤔")

            if first_if or second_if:
                return flask.redirect (flask.url_for ("users.update_password"))
            
            else:
                kursor.execute ("""UPDATE users
                SET password = (?)
                WHERE id = (?)""", [password, flask.session.get ("id")])

                connect.commit ()

                flask.flash ("Пароль змінено успішно!😊😊😊")
                return flask.redirect (flask.url_for ("home.main"))

    except KeyError:
        abort (404)




@usersapp.route ("/data", methods = ["GET", "POST"])
def data ():
    name, surname, phone, password = flask.session.get ("data")
    if flask.request.method == "POST":
        connect = sqlite3.connect ("files/tables.db")
        connect.row_factory = sqlite3.Row
        kursor = connect.cursor ()

        check = flask.request.form.get ("check")
        client = return_client ()
        ischeck = check_code (check, phone, client)

        if ischeck:
            kursor.execute ("""INSERT INTO users (name, surname, phone, password)
            VALUES (?, ?, ?, ?)
            """, [name, surname, phone, password])
            connect.commit ()
            kursor.execute ("""SELECT * FROM users
            WHERE phone == (?)
            """, [phone])
            data = kursor.fetchone ()
            del flask.session["data"]
            flask.session["islogin"] = True
            flask.session["id"] = data["id"]
            return flask.render_template ("data.html", data=data)
        elif ischeck == False:
            flask.flash ("Код введено неправильно!")
            return flask.redirect (flask.url_for ("users.register"))
        else:
            flask.flash ("Сталася помилка!")
            return flask.redirect (flask.url_for ("users.register"))