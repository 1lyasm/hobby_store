from flask import Flask, render_template, request, url_for, redirect
import psycopg2 as psql

app = Flask(__name__)


logged_in = False
cur_user = ""

def connect():
    return psql.connect(
        host="localhost",
        database="store",
        user="ilyas",
        password="password"
    )

@app.route("/")
def index():
    return redirect("/login")

@app.route("/home")
def home():
    if logged_in is False:
        return redirect("/login")
    return render_template("home.html")

@app.route("/about")
def about():
    return render_template("about.html")

def check_passw(uname, passw):
    conn = connect()
    cursor = conn.cursor()
    msg = ""
    result = True
    cursor.execute(f"select id from users where name = '{uname}';")
    id_ = cursor.fetchall()
    if len(id_) == 0:
        result = False
        msg = "Username does not exist"
    else:
        cursor.execute("select passw from passwords where id = '%s';", (id_[0]))
        correct_passw = cursor.fetchall()
        if passw != correct_passw[0][0]:
            result = False
            msg = "Password is not correct"
    cursor.close()
    conn.close()
    return result, msg

@app.route("/login", methods=('GET', 'POST'))
def login():
    msg = ""
    if request.method == "POST":
        uname, passw = request.form["uname"], request.form["passw"]
        passw_is_correct, msg = check_passw(uname, passw)
        if passw_is_correct is True:
            global logged_in
            global cur_user
            logged_in = True
            cur_user = uname
            return redirect("/home")
    return render_template("login.html", msg=msg)

def add_user(name, surname, addr, phone, passw):
    conn = connect()
    cursor = conn.cursor()

    msg = ""
    name = "'" + name + "'"
    if surname == "":
        surname = "NULL"
    else:
        surname = "'" + surname + "'"
    if addr == "":
        addr = "NULL"
    else:
        addr = "'" + addr + "'"
    if phone == "":
        phone = "NULL"
    else:
        phone = "'" + phone + "'"
    passw = "'" + passw + "'"

    cursor.execute("begin")
    try:
        cursor.execute("select nextval('users_ids')")
        next_id = cursor.fetchall()[0][0]
        cursor.execute(
            f"insert into users values({next_id}, {name}, {surname}, {addr}, {phone});")
        cursor.execute(f"insert into passwords values({next_id}, {passw});")
    except psql.errors.UniqueViolation:
        cursor.execute("rollback")
        cursor.execute(f"alter sequence users_ids restart with {next_id};")
        msg = "User already exists"
    cursor.execute("end")

    cursor.close()
    conn.close()
    return msg

@app.route("/register", methods=('GET', 'POST'))
def register():
    msg = ""
    if request.method == "POST":
        uname = request.form["uname"]
        surname = request.form["surname"]
        addr = request.form["addr"]
        phone = request.form["phone"]
        passw = request.form["passw"]

        if len(uname) == 0 or len(passw) == 0:
            msg = "Username and password can not be empty"
        else:
            msg = add_user(uname, surname, addr, phone, passw)
            if len(msg) > 0:
                return render_template("register.html", msg=msg)
            return redirect("/login")
    return render_template("register.html", msg=msg)

def fetch_info():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute('begin')
    cursor.execute(f"select name, surname, addr, phone, spent from users where name = '{cur_user}'")
    res = cursor.fetchall()[0]
    print(res)
    cursor.execute('end')
    cursor.close()
    conn.close()
    return res

@app.route("/account", methods=('GET', 'POST'))
def account():
    uname, surname, addr, phone, spent = fetch_info()
    if surname is None:
        surname = ""
    if addr is None:
        addr = ""
    if phone is None:
        phone = ""
    return render_template("account.html", uname=uname,
                           surname=surname, addr=addr, phone=phone, spent=spent)
