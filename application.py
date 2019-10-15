
import os, requests, json

from flask import Flask, session, render_template, request, redirect, url_for, jsonify
from flask_session import Session
from sqlalchemy import create_engine, text
from sqlalchemy.orm import scoped_session, sessionmaker

from functools import wraps

import setup

app = Flask(__name__)

# Check for environment variables
setup.set_environment_variables()

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if session.get('user') is None:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route("/books/")
@login_required
def search():

    params = {}
    msg = None

    for i in ['title', 'author', 'isbn']:
        try:
            params[i] = request.args[i]

            if len(params[i]) < 1:
                raise("Invalid search")

        except:
            params[i] = None

    title = params['title']
    author = params['author']
    isbn = params['isbn']

    query = text(f"SELECT title, author, isbn FROM books WHERE title ILIKE '%{title}%' OR author ILIKE '%{author}%' OR isbn ILIKE '{isbn}' ")

    books = db.execute(query).fetchall()

    if not books:

        query = text("""SELECT title, author, isbn FROM books
                ORDER BY title ASC LIMIT 20""")
        books = db.execute(query).fetchall()

        if any(params.values()):
            msg = "No books found! Perhaps you like authors from the first page of Yellow Pages?"


    return render_template("search.html", books=books, msg=msg)

@app.route("/book/<string:isbn>/", methods=["GET"])
@login_required
def book(isbn):

    # Post review to book

    data = helpers.get_book_information(isbn)

    return render_template("book.html", data=data)

@app.route("/review/add/", methods=["POST"])
@login_required
def review_add():

    user_id = int(session['user'])
    book_id = int(request.form.get('book_id'))
    isbn = request.form.get('book_isbn')
    review = request.form.get('review')

    query = text("INSERT INTO reviews (user_id, book_id, review) VALUES (:user_id, :book_id, :review)")
    db.execute(query, {'book_id': book_id, 'user_id': user_id, 'review': review})
    db.commit()

    return redirect(url_for('book', isbn=isbn))

@app.route("/register/", methods=["GET","POST"])
def register():

    if request.method == "GET":
        return render_template("register.html")

    elif request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        query = text("INSERT INTO users (username, password) VALUES (:username, :password)")
        result = db.execute(query, {'username': username, 'password': password})
        db.commit()

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
            print(result)
            session['user'] = result[0]
            return redirect(url_for('search'))
    return render_template("login.html")

@app.route("/api/<string:isbn>/")
def api(isbn):

    a = helpers.get_database_data(isbn)
    b = helpers.get_goodreads_data(isbn)

    a.update(b)

    return jsonify(a)

@app.errorhandler(404)
def error404(e):
    return render_template('404.html')

class helpers(object):

    @staticmethod
    def get_book_information(isbn):

        # Create data dict and add user info
        data = {}
        data['user'] = {}
        data['user']['id'] = session['user']

        # Add book information from DB
        data['book'] = helpers.get_database_data(isbn)

        # Add goodreads data from API
        data['goodreads'] = helpers.get_goodreads_data(isbn)

        # Get reviews for book
        data['reviews'] = helpers.get_book_reviews(data['book']['id'])

        return data

    @staticmethod
    def get_database_data(isbn):
        query = text("""SELECT * FROM books WHERE isbn = :isbn""")
        res = db.execute(query, {'isbn': isbn}).fetchone()
        if not res:
            return None
        book = {}
        book['id'] = res[0]
        book['isbn'] = res[1]
        book['title'] = res[2]
        book['author'] = res[3]
        book['year'] = res[4]
        return book

    @staticmethod
    def get_goodreads_data(isbn):
        KEY = os.getenv("GOODREADS_KEY")
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": KEY, "isbns": isbn})

        if not res:
            return None

        res = res.json()['books'][0]

        data = {}
        data['average_rating'] = res['average_rating']
        data['reviews_count'] = res['reviews_count']

        return data

    @staticmethod
    def get_book_reviews(book_id):
        query = text("""SELECT u.username, r.review, r.created
            FROM reviews r
            LEFT JOIN users u
            ON r.user_id = u.id
            WHERE r.book_id = :book_id
            """)
        res = db.execute(query, {'book_id': book_id }).fetchall()

        if not res:
            return None

        reviews = []

        for r in res:
            review = {
                'username': r[0],
                'text': r[1],
                'created': r[2]
                }
            reviews += review

        return res

if __name__ == '__main__':
    setup.set_environment_variables()
    setup.create_tables(clear=False)
    emails = []
    app.run(host="0.0.0.0", port=8888, debug=True)
