
import sys
import log_parser.db as db
import re
from geolite2 import geolite2

HOST = "https://all_to_the_bottom.com/"
DEFAULT_LOG = 'logs.txt'
DEFAULT_DATABASE = 'database.sqlite'


def main():
    log_filename = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LOG
    db_filename = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DATABASE

    database = db.connect(db_filename)
    db.initialize(database)

    with open(log_filename, 'r') as log:
        parse(log, database)

    db.finish(database)


def parse(logfile, database) -> None:
    georeader = geolite2.reader()

    for line in logfile:
        date, time, key, _, ip, action = line.split()[2:]
        datetime = date + ' ' + time
        action = parse_action(action)

        # fetching ip data is pretty slow, so we'd better do that once per ip
        if not db.has_ip_data(database, ip):
            save_ip_data(georeader, database, ip)

        db.insert_log(database, ip, datetime, action)

    georeader.close()


def save_ip_data(georeader, database, ip) -> None:
    try:
        geodata = georeader.get(ip)

        # some entries do not have "country" field
        country = (geodata["country"] or geodata["registered_country"])["names"]["ru"]
    except (KeyError, TypeError):
        country = "Unknown"
    db.insert_ip_data(database, ip, country)


# extract useful data from page address
def parse_action(action) -> str:
    if action.startswith(HOST):
        action = action[len(HOST):]

    cart_match = re.match("cart\?.*cart_id=([0-9]+)", action)
    if cart_match:
        return "CART {}".format(cart_match.group(1))

    pay_match = re.match("pay\?.*cart_id=([0-9]+)", action)
    if pay_match:
        return "PAY {}".format(pay_match.group(1))

    paid_match = re.match("success_pay_([0-9]+)\/", action)
    if paid_match:
        return "PAID {}".format(paid_match.group(1))

    return "LOOK " + action


if __name__ == "__main__":
    main()