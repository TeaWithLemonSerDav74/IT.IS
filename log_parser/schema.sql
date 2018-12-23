DROP TABLE IF EXISTS action_log;
DROP TABLE IF EXISTS ip_info;
DROP TABLE IF EXISTS carts;

CREATE TABLE IF NOT EXISTS action_log(
  ip TEXT,
  time TEXT,
  action TEXT
);

CREATE TABLE IF NOT EXISTS ip_info(
  ip TEXT,
  country TEXT
);

CREATE TABLE IF NOT EXISTS carts(
  id INTEGER,
  items TEXT,
  creation_date TEXT,
  payment_date TEXT
)