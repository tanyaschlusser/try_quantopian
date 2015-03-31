#README

How to [synchronize a forked repo] [sync] with its upstream parent:
```bash
git checkout master
git pull https://github.com/ORIGINAL_OWNER/ORIGINAL_REPO.git BRANCH_NAME
# merge if necessary
git push origin master
```

[sync]: https://help.github.com/articles/merging-an-upstream-repository-into-your-fork/

##Goals

  0. Learn some Python machine learning algorithms
  1. Learn the Quantopian API
  2. Acquire and examine external data to
     develop algorithms
  3. Demonstrate learning via a Heroku webpage


##Getting started

###Quantopian [API Overview] [overview]
Symbols:

        symbol('goog')  # single
        symbols('goog', 'fb')  # multiple
        sid(24)  # unique ID to Quantopian -- 24 is for aapl
        
- [Fundamentals] [fundamentals_reference]:
    + Available for 8000 companies, with over 670 metrics
    + Accessed using **get_fundamentals** with the same syntax as SQLAlchemy;
      returns a pandas dataframe
    + Not available during live trading, only in **before_trading_start**
      (once per day) to be stored in the **context** and used in the function
      **handle_data**
      
- [Ordering][ordering_reference]: market, limit, stop, stop limit
- [Scheduling][daterules]: frequency in days, weeks, months,
  plus order time of day in minutes
- [Allowed modules][modules]
- [Example algorithms][sample_basic]

The API is thin -- it's really just about trading. They provide
[zipline] [zipline], their backtest functions, as open-source code
([github repo][zipline-git] / [pypi page][zipline-pypi]) to test outside
of the quantopian environment. [Here is a how-to] [zipline-howto].

[zipline]: http://www.zipline.io/#quickstart
[zipline-git]: https://github.com/quantopian/zipline
[zipline-pypi]: https://pypi.python.org/pypi/zipline/0.7.0
[zipline-howto]: http://twiecki.github.io/zipline_in_the_cloud_talk

[overview]: https://www.quantopian.com/help#ide-api
[fundamentals_reference]: https://www.quantopian.com/help/fundamentals
[ordering_reference]: https://www.quantopian.com/help#ide-ordering
[daterules]: https://www.quantopian.com/help#ide-daterules
[modules]: https://www.quantopian.com/help#ide-module-import
[sample_basic]: https://www.quantopian.com/help#ide-sample-basic


###Heroku

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
**Account**

First get a [heroku](http://heroku.com) account, install the toolbelt,
and then click on the Python icon to make a Python app.

```bash
git clone https://github.com/tanyaschlusser/try_quantopian.git
cd try_quantopian
virtualenv venv
source venv/bin/activate
pip install -r requirements.txt  # so you can test locally
heroku login
heroku create
heroku apps:create tanya-try-quantopian
```

These instructions help to
[deploy in Git](https://devcenter.heroku.com/articles/git).
And we are going to copy the [Flask microblog tutorial] [flaskr]
for the main code, except use PyMongo to conncet to a MongoLab
MongoDB database instead of SQLite3 and a SQL database.

To look at the logs while the app is running:
```
    heroku logs --tail
```

[flaskr]: http://flask.pocoo.org/docs/0.10/tutorial/introduction/


**Heroku database and Mongo**

The Heroku [Postgres Hobby Tier] [heroku_hobby] has a 10,000 row limit
and the Quantcast data alone are up to 3925 rows each, so we have
to be creative and have quite a few columns if we're loading data on heroku.
The [MongoLabs developer tier] [mongolab] gives 500 free
megabyes, so we are using them.

Example URLs:
- **Postgres** postgres://<dbuser>:<dbpassword>@<hostname>:<port>/<database>
- **Mongo** mongodb://<dbuser>:<dbpassword>@<hostname>:<port>/<database> <br/>
  Where the user name and password are not for the MongoLab account, but
  whatever was set for that specific database

```bash
heroku addons:add heroku-postgresql
heroku config  # to get the database URL
# And you need to set the remote Heroku
# environment variable DATABASE_URL
heroku config:set DATABASE_URL=<the database url>
heroku config:set MONGO_URI=<the mongoDB url>
```

And then restart:
```bash
heroku restart
```

To connect to the database:
```bash
heroku pg:psql  # launch a local db connection
```

The version of Postgres on Heroku right now is 9.3.
The [Postgres 9.3 manual] [pgmanual].

[pgmanual]: http://www.postgresql.org/docs/9.3/static/
[heroku_hobby]: https://addons.heroku.com/heroku-postgresql


##Collaboration

* Quantopian: sharing a link on Sean's account
* Github repo: [Our github repo] [repo]
* Collaboration: [we have a shared IPython notebook on Sagemath] [sage]


###Sagemath cloud
By default network conenctions are disabled on the Sagemath cloud,
so you must go the 'settings' page and  email the help contact to
enable network access.

Pip is not installed on the sagemath cloud, and the user accounts
do not have root privilege, so to install libraries you should download
the actual package source code, and install from source. You need to
navigate to the 'Files' section of the page, then type a command in
the small dialog box that says `Terminal command ...`:

            curl -o pg8000.tar.gz https://pypi.python.org/packages/source/p/pg8000/pg8000-1.10.2.tar.gz#md5=7f7cfa3b4c4b103999f584ad3d813ded
            tar -xzf pg8000
            cd pg8000
            sage --python setup.py install --user

Or else you can use easy_install:

        wget https://bootstrap.pypa.io/ez_setup.py -O
        sage --python ez_setup.py --user
        easy_install --user pg8000
        easy_install --user zipline


[heroku]: https://www.heroku.com/
[repo]: https://github.com/tanyaschlusser/try_quantopian.git
[sage]: https://cloud.sagemath.com/projects/602232b7-ea8d-4575-9ee8-89139b7eb286/files/


##Data

+ [Quantquote] [qq] has a historical set with no headers. The
  [description for the second-resolution data] [qq_sec] says
  the column order is date, open, high, low, close, volume.
  All price values are adjusted for dividend and splits.

+ The [Quantquote symbols list] [qq_symbols]

+ The [Fama French] [ff] dataset hosted by Kevin French
  is already accessible via [Pandas Remote Data Access][pd_remote]
    - [Variable names from Pandas] [ff] are exactly what their names are
      in French's page 
    - [Research variables definitions] [ff__definitions] for the
      breakpoints data


[ff]: http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/data_library.html
[pd_remote]: http://pandas.pydata.org/pandas-docs/dev/remote_data.html
[ff__definitions]: http://mba.tuck.dartmouth.edu/pages/faculty/ken.french/Data_Library/variable_definitions.html
[qq]: https://quantquote.com/historical-stock-data
[qq_sec]: https://quantquote.com/docs/QuantQuote_Second.pdf
[qq_symbols]: https://quantquote.com/docs/symbol_map_comnam.csv


##Presentation

This repo is for the Heroku content that will show off algorithms and
data analysis. We will adapt
['How to make a tumblelog app using Flask + MongoEngine'][flask_mongo]
to make a blog using Flask and MongoLab.
This is [a link to mongolab] [mongolab]; chosen because
there is a free (500MB) tier for development. We've used all of the free
Heroku Postgres database for the S&P500 data.

[mongolab]: https://mongolab.com/
[flask_mongo]: http://docs.mongodb.org/ecosystem/tutorial/write-a-tumblelog-application-with-flask-mongoengine/
