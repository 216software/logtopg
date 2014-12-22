# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import psycopg2
import logging

import pkg_resources

# Started this code after reading http://stackoverflow.com/questions/20354321/is-this-postgresql-logging-handler-correct

log = logging.getLogger("logtopostgresql")

class PGHandler(logging.Handler):

    create_table_sql = None

    insert_row_sql = None

    pgconn = None

    def __init__(self, logtablename, params):

        if not params:
            raise Exception("No database where to log ☻")

        self.logtablename = logtablename

        self.__database = params['database']
        self.__host = params['host']
        self.__user = params['user']
        self.__password = params['password']

        logging.Handler.__init__(self)

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

        self.__class__.pgconn = psycopg2.connect(
            database=self.__database,
            host = self.__host,
            user = self.__user,
            password = self.__password)

    def get_create_table_sql(self):

        if not self.create_table_sql:

            self.__class__.create_table_sql = \
            pkg_resources.resource_string(
                "logtopostgresql", "createtable.sql")\
            .format(self.logtablename)

        return self.create_table_sql

    def get_insert_row_sql(self):

        if not self.insert_row_sql:

            self.__class__.insert_row_sql = \
            pkg_resources.resource_string(
                "logtopostgresql", "insertrow.sql")\
            .format(self.logtablename)

        return self.insert_row_sql


    def emit(self, record):

        self.format(record)

        print("record after formatting")
        pprint.pprint(record.__dict__)

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
