#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# try_quantopian.py
import os
import datetime
import pg8000  # Postgres database (we are using 9.3)
import urllib
import urlparse

from flask import Flask \
    ,flash, g, render_template, redirect, request \
    ,session, url_for
from flask.ext.pymongo import PyMongo 

import database

app = Flask(__name__)

app.config['AUTHOR'] = "Tanya"
app.config['MONGO_URI'] = os.environ['MONGO_URI']
app.config['PASSWORD'] = urlparse.urlparse(app.config['MONGO_URI']).password
app.config['USERNAME'] = urlparse.urlparse(app.config['MONGO_URI']).username

# app.secret_key is used by flask.session to encrypt the cookies
app.secret_key = os.urandom(24)


## ------------------------------------------------- Database parts ----- ##
mongo = PyMongo(app)

def get_db():
    """Set the flask 'g' value for _database, and return it."""
    db = getattr(g, "_database", None)
    if db is None:
        db = g._database = database.Database()
    return db

@app.teardown_appcontext
def close_connection(exception):
    """Set the flask 'g' value for _database, and return it."""
    db = getattr(g, '_database', None)
    if db is not None:
        db.close_connection()
    g._database = None


## ------------------------------------------------------ Web parts ----- ##
@app.route("/")
def show_entries():
    """Show all of the blog entries."""
    entries = mongo.db.entries.find(sort=[('$natural', -1)])
    return render_template('show_entries.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    """Add a blog post (must be logged in)."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    post = {"author": app.config['AUTHOR'],
            "title": request.form['title'],
            "text": request.form['text'],
            "date": datetime.datetime.utcnow()}
    mongo.db.entries.insert(post)
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route("/graph")
def linechart():
    """Line chart using Rickshaw. 

    data format is a list of dictionaries:
        {name:'name', data:[ {x:time, y:123}, ... {x:time, y:567}],
         color: palette.color()},
    """
    stock_data = []
    for k in request.args.keys():
        print k, ": ", request.args[k]
    if 'stocks' in request.args:
        stocks = request.args['stocks']
        stocks = [s.lower() for s in stocks.strip().split()]
    else:
        stocks = ['aapl', 'goog', 'yhoo']
    query = """
            SELECT EXTRACT (EPOCH FROM dt), {} FROM close
            WHERE dt between '2001-01-01' AND '2010-01-31';
            """
    for s in stocks:
        data = get_db().select(query.format(s), columns=('x','y'))
        if data:
            stock_data.append(dict(name=s, data=data))

    return render_template('line_chart.html', stock_data=stock_data)


@app.route('/login', methods=['GET', 'POST'])
def login():
    """Log in -- username and password taken from the MongoLabs URI."""
    error = None
    if request.method == 'POST':
        if request.form['username'] != app.config['USERNAME']:
            error = "Invalid username -- (Hint: it's your MongoLabs database username)"
        elif request.form['password'] != app.config['PASSWORD']:
            error = "Invalid password -- (Hint: it's your MongoLabs database password)"
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


@app.route('/remove')
@app.route('/remove/<post_title>')
def remove_entry(post_title=None):
    """Delete a blog post (must be logged in)."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if post_title is None:
        return redirect(url_for('show_entries'))
    else:
        post_title = post_title.decode('UTF-8')
        result = mongo.db.entries.remove({"title" : post_title})
        if result:
            flash('New entry was successfully deleted')
    return redirect(url_for('show_entries'))


@app.route('/edit')
@app.route('/edit/<post_title>', methods=['GET', 'POST'])
def edit_entry(post_title=None):
    """Update a blog post (must be logged in)."""
    if not session.get('logged_in'):
        return redirect(url_for('login'))
    if post_title is None:
        return redirect(url_for('show_entries'))
    elif request.method == 'GET':
        # If GET, show the current contents
        post_title = post_title.decode('UTF-8')
        entry = mongo.db.entries.find_one({"title" : post_title})
        if entry:
            return render_template('edit_entry.html', entry=entry)
        else:
            flash("Could not find {}".format(post_title))
            return redirect(url_for('show_entries'))
    else:  # method is 'POST'
        # If POST, perform the update or say post not found.
        post_title = post_title.decode('UTF-8')
        post = {"author": app.config['AUTHOR'],
            "title": request.form['title'],
            "text": request.form['text'],
            "date": datetime.datetime.utcnow()}
        result = mongo.db.entries.find_and_modify({"title": post_title}, post)
        if result:
            flash('New entry was successfully updated')
    return redirect(url_for('show_entries'))



if __name__ == "__main__":
    app.run(debug=True)

