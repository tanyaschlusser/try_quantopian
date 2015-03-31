#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# try_quantopian.py
import os
import pg8000  # Postgres database (we are using 9.3)
import urlparse
from flask import Flask, g, render_template, request

import database

app = Flask(__name__)


## ------------------------------------------------- Database parts ----- ##
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
def index():
    """Index page."""
    apple_march_2005 = get_db().select("""
            SELECT dt, aapl FROM spread
            WHERE dt BETWEEN %s AND %s;
        """,
        args=('2003-03-05','2003-03-08'),columns=('date', 'aapl'))
    return render_template('index.html', stock=apple_march_2005)


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

if __name__ == "__main__":
    app.run(debug=True)

