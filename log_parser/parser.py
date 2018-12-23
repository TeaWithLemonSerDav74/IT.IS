import re
import sys
from datetime import datetime

from geolite2 import geolite2

import log_parser.db as db
from log_parser.classes import Cart

HOST = "https://all_to_the_bottom.com/"
DEFAULT_LOG = 'logs.txt'
DEFAULT_DATABASE = 'database.sqlite'


def main():
    routine_start = datetime.now()

    log_filename = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_LOG
    db_filename = sys.argv[2] if len(sys.argv) > 2 else DEFAULT_DATABASE

    print("Parsing file {}; database will be stored in {}".format(log_filename, db_filename))

    database = db.connect(db_filename)
    db.initialize(database)

    with open(log_filename, 'r') as log:
        parse(log, database)

    db.finish(database)

    time_taken = datetime.now() - routine_start

    print("Done! {} seconds".format(time_taken.total_seconds()))


def parse(logfile, database) -> None:
    georeader = geolite2.reader()

    last_actions = dict()
    carts = dict()

    hits_per_hour = dict()
    hits_per_country = dict()

    for line in logfile:
        # extracting general data
        date, time, key, _, ip, action = line.split()[2:]
        date_time = date + ' ' + time
        action = parse_action(action)

        # fetching ip location is pretty slow, so we'd better do that once per ip
        country_data = db.get_ip_data(database, ip)
        if country_data:
            country = country_data[1]
        else:
            country = save_ip_data(georeader, database, ip)

        # saving record to database
        action_string = ' '.join([str(x) for x in action])
        db.insert_log(database, ip, date_time, action_string)

        # page hits stuff here
        start_hour = datetime.fromisoformat(date_time).replace(minute=0, second=0).isoformat(sep=' ')
        if start_hour in hits_per_hour:
            hits_per_hour[start_hour] += 1
        else:
            hits_per_hour[start_hour] = 1

        if country in hits_per_country:
            hits_per_country[country] += 1
        else:
            hits_per_country[country] = 1


        # handling cart stuff
        if action[0] == "CART":
            # add previously seen item in a cart

            previous_action = last_actions[ip]  # fetch that page
            cart_id = action[1]
            if cart_id not in carts:
                # create new empty cart
                carts[cart_id] = Cart(date_time)

            # we stored page address -- now is a good time to extract an item from it
            item = previous_action[1].split('/')[-2]

            carts[cart_id].add(item)

        if action[0] == "PAID":
            cart_id = action[1]
            carts[cart_id].payment_date = date_time

        last_actions[ip] = action

    db.insert_carts_data(database, carts)
    db.insert_hits_data(database, per_country=hits_per_country, per_hour=hits_per_hour)

    georeader.close()


def save_ip_data(georeader, database, ip) -> str:
    try:
        geodata = georeader.get(ip)

        # some entries do not have "country" field
        country = (geodata["country"] or geodata["registered_country"])["names"]["ru"]
    except (KeyError, TypeError, ValueError):
        country = "Нет данных"
    db.insert_ip_data(database, ip, country)
    return country


# extract useful data from page address
def parse_action(action) -> tuple:
    if action.startswith(HOST):
        action = action[len(HOST):]

    cart_match = re.match("cart\?.*cart_id=([0-9]+)", action)
    if cart_match:
        return "CART", int(cart_match.group(1))

    pay_match = re.match("pay\?.*cart_id=([0-9]+)", action)
    if pay_match:
        return "PAY", int(pay_match.group(1))

    paid_match = re.match("success_pay_([0-9]+)\/", action)
    if paid_match:
        return "PAID", int(paid_match.group(1))

    return "LOOK", action


if __name__ == "__main__":
    main()
