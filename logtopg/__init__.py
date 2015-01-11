# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import psycopg2
import logging
import textwrap
import traceback

import warnings

import pkg_resources
from psycopg2.extensions import adapt

from logtopg.version import __version__

log = logging.getLogger(__name__)

class PGHandler(logging.Handler):

    def __init__(self, log_table_name, user, password, host, database):

        logging.Handler.__init__(self)

        self.log_table_name = log_table_name

        self.database = database
        self.host = host
        self.user = user
        self.password = password

        self.pgconn = None
        self.create_table_sql = None
        self.insert_row_sql = None

    def check_if_log_table_exists(self):

        pgconn = self.get_pgconn()

        cursor = pgconn.cursor()

        cursor.execute("""
            select exists(
                select *
                from information_schema.tables
                where table_name = %s)
            """, [self.log_table_name])

        return cursor.fetchone()[0]

    def maybe_create_table(self):

        if not self.check_if_log_table_exists():

            create_table_sql = self.get_create_table_sql()

            pgconn = self.get_pgconn()

            pgconn.cursor().execute(create_table_sql)

            pgconn.commit()

            log.info("Created log table {0}.".format(self.log_table_name))

    def get_pgconn(self):

        if not self.pgconn:
            self.make_pgconn()

        return self.pgconn

    def make_pgconn(self):

        self.pgconn = psycopg2.connect(
            database=self.database,
            host = self.host,
            user = self.user,
            password = self.password)

        self.pgconn.autocommit = True

        log.info("Just made an autocommitting database connection: {0}.".format(
            self.pgconn))

    def get_create_table_sql(self):

        if not self.create_table_sql:

            self.create_table_sql = \
            pkg_resources.resource_string(
                "logtopg", "createtable.sql")\
            .decode("utf-8")\
            .format(self.log_table_name)

        return self.create_table_sql

    def get_insert_row_sql(self):

        if not self.insert_row_sql:

            self.insert_row_sql = \
            pkg_resources.resource_string(
                "logtopg", "insertrow.sql")\
            .decode("utf-8")\
            .format(self.log_table_name)

        return self.insert_row_sql


    def build_d(self, record_dict):

        d = {k:v for (k, v) in record_dict.items()
            if k in set([
                "created",
                "name",
                "levelno",
                "levelname",
                # "msg",
                "module",
                "funcName",
                "lineno",
                "exc_text",
                "process",
                "thread",
                "threadName",
                ])}

        try:
            d["msg"] = adapt(record_dict["msg"])

        except Exception as ex:
            d["msg"] = str(record_dict["msg"])

        return d

    def emit(self, record):

        self.format(record)

        if record.exc_info:
            record.exc_text = logging._defaultFormatter.formatException(record.exc_info)

        else:
            record.exc_text = ""

        if isinstance(record.msg, Exception):
            record.msg = str(record.msg)

        pgconn = self.get_pgconn()

        self.maybe_create_table()

        cursor = pgconn.cursor()

        try:

            cursor.execute(
                self.get_insert_row_sql(),
                self.build_d(record.__dict__))

        except Exception as ex:
            pass


example_dict_config = dict({

    'handlers': {
        'pg': {
            'class': 'logtopg.PGHandler',
            'level': 'DEBUG',
            'log_table_name': 'logtopg_tests',

            "database":"logtopg",
            "host":"localhost",
            "user":"logtopg",
            "password":"l0gt0pg",

        }},

    'root': {
        'handlers': ['pg'],
        'level': 'DEBUG'},

    'version': 1,

    # This is important!  Without it, any log instances created before
    # you run logging.config.dictConfig(...) will be disabled.
    'disable_existing_loggers': False,
})
