import psycopg2
import json

with open("config.json") as f:
    config = json.load(f)

db_connection = config["db_connection"]

def get_db_connection():
    return psycopg2.connect(db_connection)

def insert_stock(symbol, price):
    conn = get_db_connection()
    cur = conn.cursor()
    cur.execute("INSERT INTO stocks (symbol, price) VALUES (%s, %s)", (symbol, price))
    conn.commit()
    cur.close()
    conn.close()