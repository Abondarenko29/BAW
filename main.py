import flask
from users.users import usersapp
from login.login import loginapp
from buy.buy import buyapp
from home.home import homeapp
from towar.towar import towarapp
import sqlite3
from werkzeug.exceptions import abort
import python_files.config as config

def return_connect ():
    connect = sqlite3.connect ("files/tables.db")
    connect.row_factory = sqlite3.Row
    return connect

app = flask.Flask (__name__)
app.register_blueprint (usersapp, url_prefix = "/register")
app.register_blueprint (loginapp, url_prefix = "/login")
app.register_blueprint (buyapp, url_prefix = "")
app.register_blueprint (homeapp, url_prefix = "")
app.register_blueprint (towarapp, url_prefix = "")

app.config["SECRET_KEY"] = config.password

app.run (debug = True)