from sqlalchemy import Column, String, Integer, Date

from base import Base

class Books(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    author = db.Column(db.Integer, db.ForeignKey('authors.id'), nullable=False)

class Authors(db.Model):
    __tablename__ = 'authors'
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String, nullable=False)
    middle_name = db.Column(db.String, nullable=False)
    last_name = db.Column(db.String, nullable=False)

class Users(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=True)
    email = db.Column(db.String, nullable=False)
    date_registered = db.Column(db.DateTime)

class Likes(db.Model):
    __tablename__ = 'likes'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_type = db.Column(db.Integer, db.ForeignKey('types.id'), nullable=False)
    
class Comments(db.Model):
    __tablename__ = 'comments'
    id = db.Column(db.Integer, primary_key=True)
    user = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    target_type = db.Column(db.Integer, db.ForeignKey('types.id'), nullable=False)
                            
class ObjectTypes(db.Model):
    __tablename__ = 'type'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    created = db.Column(db.DateTime, nullable=False)