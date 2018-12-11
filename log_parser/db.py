
import sqlite3


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
        "country TEXT);"
    ]

    for query in queries:
        cur.execute(query)

    db.commit()


def insert_log(db, ip, datetime, action) -> None:
    cur = db.cursor()
    cur.execute("INSERT INTO action_log VALUES (?,?,?)", (ip, datetime, action))


def insert_ip_data(db, ip, ip_country):
    cur = db.cursor()
    cur.execute("INSERT INTO ip_info VALUES (?,?)", (ip, ip_country))


def has_ip_data(db, ip):
    cur = db.cursor()
    cur.execute("SELECT * FROM ip_info WHERE ip=?", (ip,))
    return cur.fetchone()


def finish(db):
    db.commit()
    db.close()