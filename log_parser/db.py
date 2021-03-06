
import sqlite3
import datetime

MAX_DATE = datetime.datetime.max.isoformat(' ')


def connect(filename) -> sqlite3.Connection:
    return sqlite3.connect(filename)


def initialize(db) -> None:
    cur = db.cursor()
    with open("schema.sql", 'rt') as f:
        cur.executescript(f.read())

    db.commit()


def insert_log(db, ip, datetime, action) -> None:
    cur = db.cursor()
    cur.execute("INSERT INTO action_log VALUES (?,?,?)", (ip, datetime, action))


def insert_ip_data(db, ip, ip_country) -> None:
    cur = db.cursor()
    cur.execute("INSERT INTO ip_info VALUES (?,?)", (ip, ip_country))


def get_ip_data(db, ip) -> tuple:
    cur = db.cursor()
    cur.execute("SELECT * FROM ip_info WHERE ip=?", (ip,))
    return cur.fetchone()


def insert_carts_data(db, carts) -> None:
    cur = db.cursor()
    for cart_id, cart in carts.items():
        cur.execute("INSERT INTO carts VALUES (?,?,?,?)", (
            cart_id,
            ','.join(cart.goods),
            cart.creation_date,
            cart.payment_date or MAX_DATE))


def insert_hits_data(db, per_country, per_hour):
    cur = db.cursor()
    cur.executemany("INSERT INTO hits_per_country VALUES (?,?)", list(per_country.items()))
    cur.executemany("INSERT INTO hits_per_hour VALUES (?,?)", list(per_hour.items()))


def finish(db):
    db.commit()
    db.close()
