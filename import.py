# import.py
# import books from CSV into the Databse (postresql)

import os
import csv
from sqlalchemy import create_engine, text

if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

db = create_engine(os.getenv("DATABASE_URL"))

## DROP THE TABLE IF IT EXISTS
# query = """DROP TABLE IF EXISTS books"""
# db.execute(query)

### CREATE TABLE
query = """CREATE TABLE IF NOT EXISTS books (
    id SERIAL PRIMARY KEY,
    isbn VARCHAR UNIQUE NOT NULL,
    title VARCHAR NOT NULL,
    author VARCHAR NOT NULL,
    year INTEGER
    )"""
db.execute(query)

## OPEN CSV AND INSERT TO DB
with open("books.csv", 'r') as csvfile:
    books = csv.DictReader(csvfile)
    for book in books:
        query = text("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)")
        db.execute(query, {"isbn": book['isbn'], "title" : book['title'], "author": book['author'], "year": book['year']})
