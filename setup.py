# setup.py

import os, csv
from sqlalchemy import create_engine, text

from settings import GOODREADS_KEY, DATABASE_URL


def set_environment_variables():

    def vars_exist():
        if os.getenv("DATABASE_URL") and os.getenv("GOODREADS_KEY"):
            return True
        return False

    if not vars_exist():
        # os.putenv("DATABASE_URL", DATABASE_URL)
        # os.putenv("GOODREADS_KEY", GOODREADS_KEY)
        os.environ["DATABASE_URL"] = DATABASE_URL
        os.environ["GOODREADS_KEY"] = GOODREADS_KEY

    if not vars_exist():
        raise RuntimeError("Required env variables could not be set..")

    return True

def create_tables(clear=False, cli=False):
    print("Creating tables in database")

    db = create_engine(os.getenv("DATABASE_URL"))

    # DROP THE TABLE IF IT EXISTS
    if clear:
        print("Dropping tables..")
        query = """DROP TABLE IF EXISTS users CASCADE"""
        db.execute(query)
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

    print("Creating 'books' table")
    query = text("""CREATE TABLE IF NOT EXISTS books (
        id SERIAL PRIMARY KEY,
        isbn VARCHAR UNIQUE NOT NULL,
        title VARCHAR NOT NULL,
        author VARCHAR NOT NULL,
        year INTEGER
        )""")
    db.execute(query)

    # Query database using CLI
    while cli is True:
        command = input("$psql~")
        result = db.execute(command).fetchall()
        print(result)

if __name__ == '__main__':
    create_tables(cli=True)
