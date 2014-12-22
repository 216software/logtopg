# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import psycopg2
import logging

import pkg_resources

log = logging.getLogger(__name__)

class PGHandler(logging.Handler):

    def __init__(self, logtablename, params):

        if not params:
            raise Exception("No database where to log ☻")

        logging.Handler.__init__(self)

        self.logtablename = logtablename

        self._database = params['database']
        self._host = params['host']
        self._user = params['user']
        self._password = params['password']

        self.pgconn = None
        self.create_table_sql = None
        self.insert_row_sql = None

    def maybe_create_table(self):

        create_table_sql = self.get_create_table_sql()

        pgconn = self.get_pgconn()

        pgconn.cursor().execute(create_table_sql)

        pgconn.commit()

        log.info("Just ran the SQL to create a table.")


    def get_pgconn(self):

        if not self.pgconn:
            self.make_pgconn()

        return self.pgconn

    def make_pgconn(self):

        self.pgconn = psycopg2.connect(
            database=self._database,
            host = self._host,
            user = self._user,
            password = self._password)

        log.info("Just made a database connection: {0}.".format(self.pgconn))

    def get_create_table_sql(self):

        if not self.create_table_sql:

            self.create_table_sql = \
            pkg_resources.resource_string(
                "logtopostgresql", "createtable.sql")\
            .format(self.logtablename)

        return self.create_table_sql

    def get_insert_row_sql(self):

        if not self.insert_row_sql:

            self.insert_row_sql = \
            pkg_resources.resource_string(
                "logtopostgresql", "insertrow.sql")\
            .format(self.logtablename)

        return self.insert_row_sql


    def emit(self, record):

        self.format(record)

        if record.exc_info:
            record.exc_text = logging._defaultFormatter.formatException(record.exc_info)

        else:
            record.exc_text = ""

        pgconn = self.get_pgconn()

        self.maybe_create_table()

        cursor = pgconn.cursor()

        cursor.execute(
            self.get_insert_row_sql(),
            record.__dict__)

        pgconn.commit()
