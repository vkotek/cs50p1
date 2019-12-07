# Project 1

Web Programming with Python and JavaScript

This application allows you to import a database of books, get rating information from Goodreads, and add reviews each book.

It also has an API layer where user can retrieve book information by ISBN.

## Pages

### /books/
Search for books with case-insensitive partial search

### /book/<isbn>/
Display information about a particular book. Read and write reviews.

### /login/
Login to the portal.

### /register/
Register a new user.

## API

### /api/<isbn>/
Returns the information about the book in JSON.
