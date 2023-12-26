from flask import Flask, render_template, request, url_for, redirect
import psycopg2 as psql

app = Flask(__name__)


logged_in = False
cur_user = ""
buy_id = None

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

def fetch_items():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("select items.id, items.name, users.name, n_total, n_sold,"
                   "price from items, users where items.seller = users.id")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return items

def sort_items(col_to_sort):
    conn = connect()
    cursor = conn.cursor()
    if col_to_sort == "Name":
        table_prefix = "item_name"
    elif col_to_sort == "Seller":
        table_prefix = "seller_name"
    elif col_to_sort == "Total count":
        table_prefix = "n_total"
    elif col_to_sort == "Sold count":
        table_prefix = "n_sold"
    elif col_to_sort == "Price":
        table_prefix = "price"
    cursor.execute(f"""select id, item_name, seller_name, n_total, n_sold, price
                   from {table_prefix}_sorted;""")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return items

@app.route("/home", methods=('GET', 'POST'))
def home():
    if logged_in is False:
        return redirect("/login")
    if request.method == "POST" and request.form["sort_by_form"] == "sort_by_form":
        col_to_sort = request.form["col_to_sort"]
        items = sort_items(col_to_sort)
        return render_template("home.html", items=items)
    elif request.method == "POST":
        global buy_id
        buy_id = request.form["buy_id"]
        return redirect("/buy")
    items = fetch_items()
    return render_template("home.html", items=items)

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
    cursor.execute('end')
    cursor.close()
    conn.close()
    return res

def fetch_bought():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute(f"select id from users where name = '{cur_user}';")
    cur_id = cursor.fetchall()[0][0]
    cursor.execute(f"""select distinct items.id, items.name, users.name, n_total,
                   price from items, users, buy where buy.user_id = {cur_id}
                   and buy.user_id = users.id and items.id = buy.item_id;""")
    bought = cursor.fetchall()
    cursor.execute(f"select sum(n) from buy where user_id = {cur_id}")
    n_bought = cursor.fetchall()[0][0]
    cursor.close()
    conn.close()
    return bought, n_bought

def delete_user():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("begin")
    cursor.execute(f"""delete from users where name = '{cur_user}';""")
    cursor.execute("end")
    cursor.close()
    conn.close()

@app.route("/account", methods=('GET', 'POST'))
def account():
    if request.method == "POST":
        delete_user()
        return redirect("/login")
    uname, surname, addr, phone, spent = fetch_info()
    if surname is None:
        surname = ""
    if addr is None:
        addr = ""
    if phone is None:
        phone = ""
    bought, n_bought = fetch_bought()
    return render_template("account.html", uname=uname,
                           surname=surname, addr=addr, phone=phone, spent=spent,
                           bought = bought, n_bought=n_bought)

def save_buy(count):
    conn = connect()
    cursor = conn.cursor()
    msg = ""
    cursor.execute("begin")
    try:
        cursor.execute(f"select id from users where name = '{cur_user}';")
        user_id = cursor.fetchall()[0][0];
        cursor.execute(f"select seller from items where id = {buy_id};")
        seller = cursor.fetchall()[0][0]
        if seller == user_id:
            raise AttributeError
        cursor.execute(f"insert into buy values({user_id}, {buy_id}, {count});")
    except AttributeError:
        cursor.execute("rollback")
        msg = "Can not buy from yourself"
    except:
        cursor.execute("rollback")
        msg = "That many items are not in stock, please enter smaller amount"
    cursor.execute("end")
    cursor.close()
    conn.close()
    return msg

@app.route("/buy", methods=('GET', 'POST'))
def buy():
    msg = ""
    if request.method == "POST":
        count = request.form["n_buy"]
        msg = save_buy(count)
        if len(msg) > 0:
            return render_template("buy.html", msg=msg)
        return redirect("/home")
    return render_template("buy.html", msg=msg)


def update_info(new_surn, new_addr, new_phone, new_passw):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute("begin")
    cursor.execute(f"select id from users where name = '{cur_user}';")
    cur_id = cursor.fetchall()[0][0]
    cursor.execute(f"""update users set surname = '{new_surn}', addr = '{new_addr}',
                   phone = '{new_phone}' where id = {cur_id};""")
    cursor.execute(f"""update passwords set passw = '{new_passw}'
                   where id = {cur_id};""")
    cursor.execute("end")

    cursor.close()
    conn.close()

@app.route("/change_info", methods=('GET', 'POST'))
def change_info():
    if request.method == "POST":
        new_surn = request.form["surname"]
        new_addr = request.form["addr"]
        new_phone = request.form["phone"]
        new_passw = request.form["passw"]
        update_info(new_surn, new_addr, new_phone, new_passw)
    return render_template("change_info.html")

def check_inp(name, count, price):
    msg = ""
    if len(name) == 0 or len(count) == 0 or len(price) == 0:
        msg = "Name, count, and price can not be empty"
    try:
        int(count)
        float(price)
    except:
        msg = "Count must be int and price must be decimal number"
    return msg

def add_item(name, count, price):
    conn = connect()
    cursor = conn.cursor()
    msg = ""
    cursor.execute(f"select id from users where name = '{cur_user}';")
    cur_id = cursor.fetchall()[0][0]
    cursor.execute("begin")
    try:
        cursor.execute(f"""insert into items values(nextval('items_ids'),
                   '{name}', {cur_id}, {count}, 0, {price});""")
    except:
        cursor.execute("rollback;")
        msg = "Can not have more than 3 items with same name, enter different name"
    cursor.execute("end")
    cursor.close()
    conn.close()
    return msg

@app.route("/sell", methods=('GET', 'POST'))
def sell():
    msg = ""
    if request.method == "POST":
        name = request.form["name"]
        count = request.form["count"]
        price = request.form["price"]
        msg = check_inp(name, count, price)
        if len(msg) > 0:
            return render_template("sell.html", msg=msg)
        msg = add_item(name, count, price)
        if len(msg) > 0:
            return render_template("sell.html", msg=msg)
        return redirect("/home")
    return render_template("sell.html", msg=msg)