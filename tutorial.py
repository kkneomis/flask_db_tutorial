# all the imports
import os
import sqlite3
import time
import json
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship
import flask_login

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///student.db'
db = SQLAlchemy(app)

login_manager = flask_login.LoginManager()
login_manager.init_app(app)

class Message(db.Model):
    _tablename__ = "Message"
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(140))

    category_id = db.Column(db.Integer, db.ForeignKey('category.id'))
    category = db.relationship('Category',
                               backref=db.backref('messages', lazy='dynamic'))

    def __init__(self, content, category):
        self.content = content
        self.category = category

    def __repr__(self):
        return '<Message %r>' % self.content

class Category(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))

    def __init__(self, name):
        self.name = name

    def __repr__(self):
        return '<Category %r>' % self.name



@app.route('/')
def hello_world():
    db.create_all()
    tweets = Message.query.all()
    categories = Category.query.all()
    return render_template("index.html",
                           messages=tweets,
                           categories = categories)




@app.route('/add', methods=['POST', 'GET'])
def add():
    print "ok....starting to process this form"
    message = request.form['content']
    # get the category object based on its id
    category = db.session.query(Category).get(request.form['category'])
    tweet = Message(message, category)
    db.session.add(tweet)
    db.session.commit()
    return redirect(url_for('hello_world'))


@app.route('/add_category', methods=['POST'])
def add_category():
    name = request.form['category']
    category = Category(name)
    db.session.add(category)
    db.session.commit()
    return redirect(url_for('hello_world'))


# Our mock database.
users = {'foo@bar.tld': {'pw': 'secret'}}

class User(flask_login.UserMixin):
    pass


@login_manager.user_loader
def user_loader(email):
    if email not in users:
        return

    user = User()
    user.id = email
    return user


@login_manager.request_loader
def request_loader(request):
    email = request.form.get('email')
    if email not in users:
        return

    user = User()
    user.id = email

    # DO NOT ever store passwords in plaintext and always compare password
    # hashes using constant-time comparison!
    user.is_authenticated = request.form['pw'] == users[email]['pw']

    return user

if __name__ == '__main__':
    app.run()
