# IT.IS

Solution for a test task.

## Log parser

### Requirements

Python 3.7+ with following additional packages:
- maxminddb-geolite2

### Usage

Go to `log_parser` folder, then
```bash
python3 parser.py [log file] [database file]
```
will parse _log file_, create _database file_ if it doesn't exist and fill it with data.
Defaults:
 - _log file_ is `logs.txt`
 - _database file_ is `database.sqlite`

## Web interface

Not implemented yet.