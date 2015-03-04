README
######

Goals
=====

  0. Learn some Python machine learning algorithms
  1. Learn the Quantopian API
  2. Acquire and examine external data to
     develop algorithms
  3. Demonstrate learning via a Heroku webpage


Getting started
===============

Quantopian [API Overview] [overview]

[overview]: https://www.quantopian.com/help#ide-api


Heroku
------

**Virtual environment**
To be sure of the environment we can use virtualenv in
our repository directory

```bash
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt
## to deactivate the virtual environment,
## just type 'deactivate' (without quotes)
```


**Heroku database**
First get a [heroku](http://heroku.com) account, and then click on the Python icon to make a Python app.

These instructions help to
[deploy in Git](https://devcenter.heroku.com/articles/git).

There is an issue with storing passwords in a configuration
file -- you can't just add files to your Heroku repo, you
are supposed to use environment variables.
To add an environment variable to Heroku:

    heroku config:set DATABASE=<database value>
    heroku config:set HOST=<host value (ec2-something.amazon.com)>
    heroku config:set PORT=5432
    heroku config:set USER=<user name>
    heroku config:set PASSWORD=<password>


And then restart:

    heroku restart

To look at the logs while the app is running:

    heroku logs --tail




Github repo


Sagemath link
https://cloud.sagemath.com/projects/602232b7-ea8d-4575-9ee8-89139b7eb286/files/




[heroku]: https://www.heroku.com/


Collaborative exploration
=========================

A shared IPython notebook and workspace for this project is hosted on https://cloud.sagemath.com


Presentation
============

This repo is for the Heroku content to show off algorithms and data analysis. 