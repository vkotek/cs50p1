
import os, requests

from flask import Flask, session, render_template, request, redirect, url_for
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

import settings

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def login_required(func):
    def wrapper_login_required():
        if session.get('user') is None:
            return redirect(url_for('login'))
    return wrapper_login_required

@app.route("/books/")
@login_required
def search():

    # title = request.args['title']
    # author = request.args['author']
    # isbn = request.args['isbn']
    params = {}

    for i in ['title', 'author', 'isbn']:
        try:
            params[i] = request.args[i]
        except:
            params[i] = None

    query = text("""SELECT title, author, isbn FROM books
            WHERE title LIKE :title
            OR author LIKE :author
            OR isbn LIKE :isbn""")
    books = db.execute(query, {'title': params['title'], 'author': params['author'], 'isbn': params['isbn']}).fetchall()
    return render_template("search.html", books=books)

@app.route("/book/<string:isbn>/", methods=["GET", "POST"])
@login_required
def book(isbn):

    if request.method == "POST":
        user_id = session['user']
        book_id = request.form.get('book_id')
        review = request.form.get('review')

        query = text("INSERT INTO review (user_id, book_id, review) VALUES (:user_id, :book_id, :review)")
        db.execute(query, {'user_id': user_id})
        return redirect(url_for('book'), isbn=isbn)

    data = {}
    data['user'] = {}
    data['user']['id'] = session['user']

    # Get the book from DB and map it to dict
    query = text("""SELECT * FROM books WHERE isbn = :isbn""")
    res = db.execute(query, {'isbn': isbn}).fetchone()
    data['book'] = {}
    data['book']['id'] = res[0]
    data['book']['isbn'] = res[1]
    data['book']['title'] = res[2]
    data['book']['author'] = res[3]
    data['book']['published'] = res[4]

    # Get goodreads data
    KEY = settings.GOODREADS_KEY
    res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": isbn})
    res = res.json()['books'][0]
    data['goodreads'] = {}
    data['goodreads']['average'] =  res['average_rating']
    data['goodreads']['count'] =  res['ratings_count']

    # Get reviews for book
    query = text("""SELECT * FROM reviews WHERE book_id = :book_id""")
    res = db.execute(query, {'book_id': data['book']['id'] })
    data['reviews'] = res.fetchall()

    print(data)
    return render_template("book.html", data=data)

@app.route("/review/add/", methods=["POST"])
@login_required
def review_add():
    user_id = session['user']
    book_id = request.form.get('book_id')
    isbn = request.form.get('book_isbn')
    review = request.form.get('review')

    query = text("INSERT INTO review (user_id, book_id, review) VALUES (:user_id, :book_id, :review)")
    db.execute(query, {'user_id': user_id})
    return redirect(url_for('book', isbn=isbn))

@app.route("/register/", methods=["GET","POST"])
def register():

    create_tables()

    if request.method == "GET":
        return render_template("register.html")

    elif request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        query = text("INSERT INTO users (username, password) VALUES (:username, :password)")
        print(query)
        result = db.execute(query, {'username': username, 'password': password})
        print(result)
        return redirect(url_for('login'))

@app.route("/logout/")
@login_required
def logout():
    if session.get('user') is not None:
        session.pop('user')
        return redirect(url_for('login'))
    return render_template("index.html", data=data)

@app.route("/login/", methods=["GET","POST"])
def login():
    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')
        query = text("SELECT id FROM users WHERE username = :username AND password = :password")
        result = db.execute(query, {'username': username, 'password': password}).fetchone()
        if result:
            session['user'] = id
            return redirect(url_for('search'))
    return render_template("login.html")

@app.route("/api/")
def api():
    return render_template("index.html", data=data)

if __name__ == '__main__':
    emails = []
    app.run(host="0.0.0.0", port=8888, debug=True)
