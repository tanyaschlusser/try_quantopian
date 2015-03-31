#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# try_quantopian.py
import os
import datetime
import pg8000  # Postgres database (we are using 9.3)
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
    coll = mongo.db.entries
    entries = mongo.db.entries.find(sort=[('$natural', -1)])
    return render_template('show_entries.html', entries=entries)


@app.route("/scratch")
def scratch():
    """Junk I don't want to delete."""
    # cur = g.db.execute('select title, text from entries order by id desc')
    # entries = [dict(title=row[0], text=row[1]) for row in cur.fetchall()]
    # 
    # apple_march_2005 = get_db().select("""
    #         SELECT dt, aapl FROM spread
    #         WHERE dt BETWEEN %s AND %s;
    #     """,
    #     args=('2003-03-05','2003-03-08'),columns=('date', 'aapl'))
    # mongo_collections = mongo.db.collection_names()
    # return render_template('index.html', stock=apple_march_2005, mongo_collections=mongo_collections)


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
    print "REQUEST.args:", request.args
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


if __name__ == "__main__":
    app.run(debug=True)

