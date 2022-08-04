import sqlite3

#User: sap@gentor.com
#Password: z7vxfFR4Y6PgmDsq

DB_PATH = "h2h.db"

def set_cursor():
    cxn = sqlite3.connect(DB_PATH)
    return cxn.cursor()


def parse_one(row=(), description = ()):
    data = {}
    i = 0
    for key in description:
        data[key[0]] = row[i]
        i += 1

    return data


def fetchone(sql="select @@version"):
    cursor = set_cursor()
    row = cursor.execute(sql).fetchone()
    if row is not None:
        row = parse_one(row, cursor.description)
    cursor.close()
    return row
