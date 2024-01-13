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
                   "price, color from items, users where items.seller = users.id")
    items = cursor.fetchall()
    cursor.close()
    conn.close()
    return items

def sort_items(col_to_sort):
    conn = connect()
    cursor = conn.cursor()

    items = []
    if (len(col_to_sort) > 0):
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
        cursor.execute(f"""select id, item_name, seller_name, n_total, n_sold, price, color
                        from {table_prefix}_sorted;""")
        items = cursor.fetchall()

    cursor.close()
    conn.close()
    return items

def search(query):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(f"select * from search('%{query}%')")
    items = cursor.fetchall()
    print(f"search: items: {items}")

    cursor.close()
    conn.close()
    return items


def filter_by_color(color):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(f"select * from filter_by_color('{color}')")
    items = cursor.fetchall()
    print(f"filter_by_color: items: {items}")

    cursor.close()
    conn.close()

    return items


@app.route("/home", methods=('GET', 'POST'))
def home():
    if logged_in is False:
        return redirect("/login")

    if request.method == "POST" and "sort_by_form" in request.form.keys():
        col_to_sort = request.form["col_to_sort"]
        items = sort_items(col_to_sort)
        return render_template("home.html", items=items)

    elif request.method == "POST" and "search_form" in request.form.keys():
        query = request.form["query"]
        items = search(query)
        return render_template("home.html", items=items)

    elif request.method == "POST" and "filter_by_color_form" in request.form.keys():
        color = request.form["color_to_filter"]
        items = filter_by_color(color)
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
        login_button = request.form.get("login_button")
        reg_button = request.form.get("reg_button")

        if login_button is not None:
            uname, passw = request.form["uname"], request.form["passw"]
            passw_is_correct, msg = check_passw(uname, passw)
            if passw_is_correct is True:
                global logged_in
                global cur_user
                logged_in = True
                cur_user = uname
                return redirect("/home")
        elif reg_button is not None:
            return redirect("/register")

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
            msg = "Name/password are required"
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
    cursor.execute(f"select sum(n) from buy where user_id = {cur_id} group by item_id")
    n_bought = cursor.fetchall()
    dict_ = {key_: val_[0] for (key_, val_) in zip(bought, n_bought)}
    print(dict_)

    cursor.close()
    conn.close()
    return dict_


def delete_user():
    conn = connect()
    cursor = conn.cursor()
    cursor.execute("begin")
    cursor.execute(f"""delete from users where name = '{cur_user}';""")
    cursor.execute("end")
    cursor.close()
    conn.close()


def fetch_duplicate_named_items():
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(f"""select items.name from buy, items, users
                   where items.id = item_id and users.id = user_id
                        and users.name = '{cur_user}'
                   group by items.name having count(distinct item_id) > 1""")
    cursor_res = cursor.fetchall()
    print(f"fetch_duplicate_named_items: cursor_res: {cursor_res}")
    duplicates = []
    if (len(cursor_res) > 0):
        duplicates = cursor_res

    cursor.close()
    conn.close()

    return duplicates


@app.route("/account", methods=('GET', 'POST'))
def account():
    if request.method == "POST":
        delete_ = request.form.get("delete_button")
        change_ = request.form.get("change_button")

        if delete_ is not None:
            delete_user()
            return redirect("/login")
        elif change_ is not None:
            return redirect("/change_info")

    uname, surname, addr, phone, spent = fetch_info()
    if surname is None:
        surname = ""
    if addr is None:
        addr = ""
    if phone is None:
        phone = ""
    dict_ = fetch_bought()
    duplicates = fetch_duplicate_named_items()
    return render_template("account.html", uname=uname,
                           surname=surname, addr=addr, phone=phone, spent=spent,
                           dict_=dict_, duplicates=duplicates)

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
        cursor.execute(f"select spent from users where id = {user_id}")
        old_spent = cursor.fetchall()[0][0]
        cursor.execute(f"select n_sold from items where id = {buy_id}")
        old_n_sold = cursor.fetchall()[0][0]
        cursor.execute(f"insert into buy values(nextval('buy_sequence'), {user_id}, {buy_id}, {count});")
        cursor.execute(f"select spent from users where id = {user_id}")
        new_spent = cursor.fetchall()[0][0]
        cursor.execute(f"select n_sold from items where id = {buy_id}")
        new_n_sold = cursor.fetchall()[0][0]
        msg += f"Sold count of {buy_id} numbered item went from {old_n_sold} to {new_n_sold}. "
        msg += f"Amount spent went from {old_spent} to {new_spent}."
    except AttributeError as e:
        print(e)
        cursor.execute("rollback")
        msg = "Can not buy from yourself"
    except Exception as e:
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
        return redirect("/buy")
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

def add_item(name, count, price, color):
    conn = connect()
    cursor = conn.cursor()

    msg = ""
    cursor.execute(f"select id from users where name = '{cur_user}';")
    cur_id = cursor.fetchall()[0][0]
    cursor.execute("begin")
    try:
        cursor.execute(f"""insert into items values(nextval('items_ids'),
                   '{name}', {cur_id}, {count}, 0, {price}, '{color}');""")
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
        color = request.form["color"]
        msg = check_inp(name, count, price)
        if len(msg) > 0:
            return render_template("sell.html", msg=msg)
        msg = add_item(name, count, price, color)
        if len(msg) > 0:
            return render_template("sell.html", msg=msg)
        return redirect("/home")
    return render_template("sell.html", msg=msg)

def fetch_stat(stat):
    if len(stat) < 1:
        return ""

    conn = connect()
    cursor = conn.cursor()

    res = None

    print(f"fetch_stat: stat: {stat}")

    if stat == "Min":
        cursor.execute(f"select price from items order by price asc limit 1")
        res = cursor.fetchall()[0][0]
    elif stat == "Max":
        cursor.execute(f"select price from items order by price desc limit 1")
        res = cursor.fetchall()[0][0]
    elif stat == "Count":
        cursor.execute(f"select count(*) from items")
        res = cursor.fetchall()[0][0]
    elif stat == "Average":
        cursor.execute(f"select avg(price) from items")
        res = cursor.fetchall()[0][0]
    elif stat == "Sum":
        cursor.execute(f"select sum(price) from items")
        res = cursor.fetchall()[0][0]
    else:
        raise Exception

    if res is not None:
        res = round(res, 2)
        res = f"{stat}: {res}"

    cursor.close()
    conn.close()

    return res


def fetch_items_in_range(min_, max_):
    conn = connect()
    cursor = conn.cursor()

    cursor.execute(f"select * from fetch_items_in_range({min_}, {max_})")
    items = cursor.fetchall()

    cursor.close()
    conn.close()

    return items


@app.route("/stats", methods=('GET', 'POST'))
def stats():
    res = ""

    if request.method == "POST" and "stats_form" in request.form.keys():
        stat = request.form["stat"]
        res = fetch_stat(stat)
        return render_template("stats.html", res=res, items=[])

    elif request.method == "POST" and "range_form" in request.form.keys():
        min_ = request.form["min_price"]
        max_ = request.form["max_price"]
        items = fetch_items_in_range(min_, max_)
        return render_template("stats.html", res="", items=items)

    return render_template("stats.html", res=res)

