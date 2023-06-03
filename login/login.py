import flask
import sqlite3
from werkzeug.exceptions import abort

loginapp = flask.Blueprint ("login", __name__,
                            template_folder = "templates",
                            static_folder = "static")

def login ():
    return flask.render_template ("login.html")
loginapp.add_url_rule ("/in", "login", login)

@loginapp.route("/endin", methods = ["GET", "POST"])
def endin ():
    if flask.request.method == "POST":
        id_ = flask.request.form.get ("id")
        password = flask.request.form.get ("password")

        connect = sqlite3.connect ("files/tables.db")
        kursor = connect.cursor ()
        kursor.execute ("""
            SELECT * FROM users
            WHERE id == (?) AND
            password == (?)
        """, [id_, password])
        kursor.execute ("""
            SELECT password FROM users
            WHERE id == (?)
        """, [id_])

        wpassword = kursor.fetchone ()

        if wpassword is None:
            flask.flash ("Такого обліпкового запису не існує!")
            return flask.redirect (flask.url_for ("login.login"))

        elif wpassword[0] != password:
            flask.flash ("Пароль введено не правильно!")
            return flask.redirect (flask.url_for ("login.login"))

        else:
            flask.session["islogin"] = True
            flask.session["id"] = id_
            return flask.redirect (flask.url_for ("home.main"))
        
def logout ():
    try:
        if flask.session.get ("islogin"):
            flask.session ["islogin"] = False
            flask.session ["id"] = None
            return flask.redirect (flask.url_for ("home.index"))
        else:
            abort (404)
    except:
        flask.redirect (flask.url_for ("home.index"))
loginapp.add_url_rule ("/logout", "logout", logout, methods = ["POST", "GET"])