# import.py
# import books from CSV into the Databse (postresql)

import os
import csv
from sqlalchemy import create_engine, text

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

db = create_engine(os.getenv("DATABASE_URL"))

## DROP THE TABLE IF IT EXISTS
# query = """DROP TABLE IF EXISTS users"""
# db.execute(query)
#
# query = """DROP TABLE IF EXISTS reviews"""
# db.execute(query)

query = text("""CREATE TABLE IF NOT EXISTS users (
        id SERIAL PRIMARY KEY,
        username VARCHAR,
        password VARCHAR
        )""")
db.execute(query)

query = text("""CREATE TABLE IF NOT EXISTS reviews (
        id SERIAL PRIMARY KEY,
        book_id INTEGER REFERENCES users,
        user_id INTEGER REFERENCES users,
        review VARCHAR,
        created TIMESTAMP
        )""")
db.execute(query)

## Query database using CLI
# while True:
#     command = input("$psql~")
#     result = db.execute(command).fetchall()
#     print(result)
