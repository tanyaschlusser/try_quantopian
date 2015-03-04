#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# try_quantopian.py
import os
import pg8000  # Postgres database (we are using 9.3)
import urlparse
from flask import Flask


urlparse.uses_netloc.append("postgres")
url = urlparse.urlparse(os.environ["DATABASE_URL"])

def connect_db():
    return pg8000.connect(
            database=url.path[1:],
            host=url.hostname,
            port=url.port,
            user=url.username,
            password=url.password,
            ssl=True
            )   


app = Flask(__name__)

@app.route("/")
def index():
    return "Hello World"

if __name__ == "__main__":
    app.run()

