# -*- coding: utf-8 -*-
#
# database.py
import pg8000
import urlparse

## ------------------------------------------------- Database parts ----- ##
urlparse.uses_netloc.append("postgres")
__url = urlparse.urlparse(os.environ["DATABASE_URL"])


class Database:
    def __init__(self):
        self._connect_db()

    def _connect_db(self):
        self.db = pg8000.connect(
                database=__url.path[1:],
                host=__url.hostname,
                port=__url.port,
                user=__url.username,
                password=__url.password,
                ssl=True
            )   

    def close_connection(self):
        if self.db is not None:
            self.db.close()
        self.db = None


    def query(self, q, args=None, commit=False):
        """Perform a query returning the database cursor if success else None.

        Use db_select for SELECT queries.
        Wrap the query with a try/except, catch the error, and return
        False if the query fails.
        """
        if self.db is None:
            self._connect_db()
        cur = self.db.cursor()
        try:
            cur.execute(q, args)
            if commit:
                self.db.commit()
        except pg8000.ProgrammingError as e:
            print "error:", e
            raise
        return cur


    def select(self, q, args=None, columns=None):
        """Return the result of a select query as an array of dictionaries.

        Each dictionary has keys taken from the 'columns' argument, or else
        'col0' ... 'colN-1' for the N columns returned.

        If there is an error with the query, return None.

        Keyword arguments
        args -- passed to pg8000.cursor.execute() for a secure
                parameterized query.
                We use the default format: SELECT * FROM TABLE WHERE col1 = '%s'
        """
        try:
            cur = self.query(q, args=args)
            if cur is None:
                return None
            else:
                results = cur.fetchall()
                cur.close()
        except pg8000.ProgrammingError as e:
            print "error:", e
            self.db.rollback()
            if cur is not None:
                cur.close()
            raise
        if results is None or len(results) == 0:
            return None
        elif len(results[0]) > len(columns):
            columns = list(columns) + [
                    "col%d" % i for i in range(len(columns),len(results))]
        elif len(results[0]) < len(columns):
            columns = columns[0:len(results[0])]

        return [dict(zip(columns, result)) for result in results]


    def select_one(self, q, args=None, columns=None):
        """Return the one-row result of a select query as a dictionary.

            If there are more than one rows, return only the contents of
            the first one. If there are no rows, return None.
        """
        rows = self.select(q, args=args, columns=columns)
        if rows is None or len(rows) == 0:
            return {}
        return rows[0]
