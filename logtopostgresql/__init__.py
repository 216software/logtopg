# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import psycopg2
import logging
import textwrap
import time

import pkg_resources

# Ganked from http://stackoverflow.com/questions/20354321/is-this-postgresql-logging-handler-correct

log = logging.getLogger("logtopostgresql")

class psqlHandler(logging.Handler):

    insertion_sql = textwrap.dedent("""
        INSERT INTO {} (
            Created,
            Name,
            LogLevel,
            LogLevelName,
            Message,
            Module,
            FuncName,
            LineNo,
            Exception,
            Process,
            Thread,
            ThreadName
        ) VALUES (
            %(created)s,
            %(name)s,
            %(levelno)s,
            %(levelname)s,
            %(msg)s,
            %(module)s,
            %(funcName)s,
            %(lineno)s,
            %(exc_text)s,
            %(process)s,
            %(thread)s,
            %(threadName)s
        );
        """)

    def connect(self):

        self.pgconn = psycopg2.connect(
            database=self.__database,
            host = self.__host,
            user = self.__user,
            password = self.__password)

    def get_create_table_sql(self):

        return pkg_resources.resource_string(
            "logtopostgresql", "createtable.sql").format(
                self.logtablename)

    def __init__(self, logtablename, params):

        if not params:
            raise Exception("No database where to log ☻")

        self.logtablename = logtablename

        self.__database = params['database']
        self.__host = params['host']
        self.__user = params['user']
        self.__password = params['password']

        self.connect()

        logging.Handler.__init__(self)

        create_table_sql = self.get_create_table_sql()

        self.pgconn.cursor().execute(create_table_sql)

        self.pgconn.commit()

        log.info("Just ran the SQL to create a table.")

    def emit(self, record):

        # Use default formatting:
        self.format(record)

        # print(record.created)
        # print(type(record.created))

        if record.exc_info:
            record.exc_text = logging._defaultFormatter.formatException(record.exc_info)

        else:
            record.exc_text = ""

        cur = self.pgconn.cursor()

        cur.execute(
            psqlHandler.insertion_sql.format(
                self.logtablename),
                record.__dict__)

        self.pgconn.commit()
        self.pgconn.cursor().close()

