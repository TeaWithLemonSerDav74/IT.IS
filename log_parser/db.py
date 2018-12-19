
import sqlite3
import datetime

MAX_DATE = datetime.datetime.max.isoformat(' ')


def connect(filename) -> sqlite3.Connection:
    return sqlite3.connect(filename)


def initialize(db) -> None:
    cur = db.cursor()
    queries = [
        "CREATE TABLE IF NOT EXISTS action_log("
        "ip TEXT,"
        "time TEXT,"
        "action TEXT);",

        "CREATE TABLE IF NOT EXISTS ip_info("
        "ip TEXT,"
        "country TEXT);",

        "CREATE TABLE IF NOT EXISTS carts("
        "id INTEGER,"
        "items TEXT,"
        "creation_date TEXT,"
        "payment_date TEXT)"
    ]

    for query in queries:
        cur.execute(query)

    db.commit()


def insert_log(db, ip, datetime, action) -> None:
    cur = db.cursor()
    cur.execute("INSERT INTO action_log VALUES (?,?,?)", (ip, datetime, action))


def insert_ip_data(db, ip, ip_country) -> None:
    cur = db.cursor()
    cur.execute("INSERT INTO ip_info VALUES (?,?)", (ip, ip_country))


def has_ip_data(db, ip) -> tuple:
    cur = db.cursor()
    cur.execute("SELECT * FROM ip_info WHERE ip=?", (ip,))
    return cur.fetchone()


def save_cart_data(db, carts) -> None:
    cur = db.cursor()
    for cart_id, cart in carts.items():
        cur.execute("INSERT INTO carts VALUES (?,?,?,?)", (
            cart_id,
            ','.join(cart.goods),
            cart.creation_date,
            cart.payment_date or MAX_DATE))


def finish(db):
    db.commit()
    db.close()
