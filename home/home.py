import flask
import sqlite3
from werkzeug.exceptions import abort

def return_connect ():
    connect = sqlite3.connect ("files/tables.db")
    connect.row_factory = sqlite3.Row
    return connect

homeapp = flask.Blueprint ("home", __name__,
    template_folder = "templates",
    static_folder = "static"
)

# @homeapp.route("/test")
# def test ():
#     connect = sqlite3.connect ("files/tables.db")
#     kursor = connect.cursor ()

#     kursor.execute ("""SELECT * FROM users""")
#     users = kursor.fetchall ()

#     kursor.execute ("""SELECT * FROM price""")
#     price = kursor.fetchall ()

#     kursor.execute ("""SELECT * FROM bank""")
#     bank = kursor.fetchall ()

#     kursor.execute ("""SELECT * FROM users_price""")
#     users_price = kursor.fetchall ()

#     kursor.execute ("""SELECT * FROM price_bank""")
#     price_bank = kursor.fetchall ()

#     return f"""users:<br>
#     {str(users)}<br>
#     ----------------------------------------------------------------<br>
#     price:<br>
#     {str(price)}<br>
#     ----------------------------------------------------------------<br>
#     bank:<br>
#     {str(bank)}<br>
#     ----------------------------------------------------------------<br>
#     users_price:<br>
#     {str(users_price)}<br>
#     ----------------------------------------------------------------<br>
#     price_bank:<br>
#     {str(price_bank)}<br>
#     """

def index ():
    # flask.session["islogin"] = False
    # flask.session["id"] = None
    try:
        if flask.session["islogin"]:
            return flask.redirect (flask.url_for ("main"))
        else:
            flask.session["islogin"] = False
            flask.session["id"] = None
            return flask.render_template ("index.html")
    except:
        flask.session["islogin"] = False
        flask.session["id"] = None
        return flask.render_template ("index.html")
homeapp.add_url_rule ("/", "index", index)

@homeapp.route("/main", methods=["GET", "POST"])
def main ():
    try:
        if flask.session.get ("islogin"):
            connect = return_connect ()
            kursor = connect.cursor ()

            a = flask.request.args.get ("category")

            # kursor.execute ("""SELECT id FROM price
            # ORDER BY datetime DESC""")
            # iD = kursor.fetchall ()
            # for i in iD:
            #     print (i["id"])

            kursor.execute ("""SELECT price.id, price.price, price.currency, price.name, price.amount, REPLACE(price.writing, '\n', '<br>') AS writing,
            users.phone, users.id as u_id FROM price
            JOIN users_price ON price.id = users_price.id_price
            JOIN users ON users.id = users_price.id_users
            GROUP BY price.id
            ORDER BY price.datetime DESC""")
            datas = kursor.fetchmany (100)

            id_user = int (flask.session.get ("id"))

            return flask.render_template ("main.html", datas=datas, id_user = id_user)
        else:
            abort (404)
    except KeyError:
        abort (404)

@homeapp.route ("/main?category=<category>", methods=["GET", "POST"])
def category (category):
    try:
        if flask.session.get ("islogin"):
            connect = return_connect ()
            kursor = connect.cursor ()

            # kursor.execute ("""SELECT id FROM price
            # ORDER BY datetime DESC""")
            # iD = kursor.fetchall ()
            # for i in iD:
            #     print (i["id"])

            kursor.execute ("""SELECT price.id, price.price, price.currency, price.name, price.amount, REPLACE(price.writing, '\n', '<br>') AS writing,
            users.phone, users.id as u_id FROM price
            JOIN users_price ON price.id = users_price.id_price
            JOIN users ON users.id = users_price.id_users
            WHERE category = (?)
            GROUP BY price.id
            ORDER BY price.datetime DESC
            """, [category])
            datas = kursor.fetchmany (100)

            id_user = int (flask.session.get ("id"))

            return flask.render_template ("main.html", datas=datas, id_user = id_user)
        else:
            abort (404)
    except KeyError:
        abort (404)

def search ():
    try:
        if flask.request.method == "POST" and flask.session.get ("islogin"):
            look_for = flask.request.args.get ("look_for")
            connect = return_connect ()
            kursor = connect.cursor ()

            kursor.execute ("""SELECT price.price, price.id, price.currency, price.name, price.amount, price.writing,
            users.phone FROM users, price, users_price
            WHERE price.name == (?)
            ORDER BY price.datetime DESC""", [look_for])
            datas = kursor.fetchall ()
            if datas == []:
                flask.flash ("Нічого не знайдено 😥😥😥!")
            return flask.render_template ("main.html", datas = datas)
        else:
            abort (404)
    except KeyError:
        abort (404)
homeapp.add_url_rule ("/search", "search", search, methods = ["GET", "POST"])

def check_number ():
    return flask.render_template ("check_your_number.html")

@homeapp.route("/info/price")
def towar_info ():
    try:
        if flask.session.get ("islogin"):
            id_ = flask.request.args.get ("id")
            connect = return_connect ()
            kursor = connect.cursor ()
            kursor.execute ("""SELECT price.name, price.price, price.id, price.amount, price.currency, price.writing, price.category,
            users.surname, users.name AS pricer_name, users.phone
            FROM price
            JOIN users_price ON price.id = users_price.id_price
            JOIN users ON users.id = users_price.id_users
            WHERE price.id == (?)""", [id_])
            data = kursor.fetchone ()

            writing = data["writing"].replace ("&lt", "<")
            writing = writing.replace ("&gt", ">")

            return flask.render_template ("price_info.html", data = data, writing=writing)
        else:
            abort (404)
    except KeyError:
        abort (404)

@homeapp.route("/info")
def user_info ():
    try:
        if flask.session.get ("islogin"):
            connect = return_connect ()
            kursor = connect.cursor ()
            kursor.execute ("""
                SELECT * FROM users
                WHERE id == (?)
            """, [flask.session.get ("id")])
            data = kursor.fetchone ()
            return flask.render_template ("data.html", data=data)
        else:
            abort (404)
    except KeyError:
        abort (404)