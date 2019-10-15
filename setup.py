# import.py
# import books from CSV into the Databse (postresql)

import os
import csv
from sqlalchemy import create_engine, text
import settings


def set_environment_variables():
    print("Setting up environment variables")
    if not os.getenv("DATABASE_URL"):
        os.putenv("DATABASE_URL", settings.DATABASE_URL)
    return True

def create_tables(clear=False, cli=False):
    print("Creating tables in database")

    db = create_engine(os.getenv("DATABASE_URL"))

    # DROP THE TABLE IF IT EXISTS
    if clear:
        print("Dropping tables..")
        #query = """DROP TABLE IF EXISTS users CASCADE"""
        #db.execute(query)
        query = """DROP TABLE IF EXISTS reviews CASCADE"""
        db.execute(query)

    print("Creating 'users' table")
    query = text("""CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username VARCHAR,
            password VARCHAR,
            created TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            )""")
    db.execute(query)

    print("Creating 'reviews' table")
    query = text("""CREATE TABLE IF NOT EXISTS reviews (
            id SERIAL PRIMARY KEY,
            book_id INTEGER REFERENCES books,
            user_id INTEGER REFERENCES users,
            review VARCHAR,
            created TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT NOW()
            )""")
    db.execute(query)

    # Query database using CLI
    while cli is True:
        command = input("$psql~")
        result = db.execute(command).fetchall()
        print(result)

if __name__ == '__main__':
    create_tables(cli=True)
