# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:


import logging
import os
import subprocess
import textwrap
import traceback
import warnings

import pkg_resources
import psycopg2
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

            out = run_sql_commands(create_table_sql, self.user, self.password,
                self.host, self.database)

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

            s = \
            pkg_resources.resource_string(
                "logtopg", "createtable.sql")\
            .decode("utf-8")\
            .format(self.log_table_name)

            self.create_table_sql = s.encode("utf-8")

        return self.create_table_sql

    def get_insert_row_sql(self):

        """
        Cache the insert query (with placeholder parameters) in memory
        so that every log.... call doesn't do file IO.
        """

        if not self.insert_row_sql:

            self.insert_row_sql = \
            pkg_resources.resource_string(
                "logtopg", "insertrow.sql")\
            .decode("utf-8")\
            .format(self.log_table_name)

        return self.insert_row_sql

    def build_d(self, record_dict):

        d = record_dict

        # Catch messages that can't be adapted as-is, and convert it to
        # strings
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

        cursor.execute(
            self.get_insert_row_sql(),
            self.build_d(record.__dict__))


example_dict_config = dict({

    "loggers": {
        "logtopg": {
            # "handlers": ["pg", "console"],
            "handlers": ["console"],
            "level": "DEBUG",
        }
    },

    'handlers': {
        'pg': {
            'class': 'logtopg.PGHandler',
            'level': 'DEBUG',
            'log_table_name': 'logtopg_logs',

            "database":"logtopg",
            "host":"localhost",
            "user":"logtopg",
            "password":"l0gt0pg",
        },

        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "formatter": "consolefmt",
        },

    },

    "formatters": {
            "consolefmt":{
                "format": '%(asctime)-22s [%(process)d] %(name)-30s %(lineno)-5d %(levelname)-8s %(message)s',
            },
    },

    # Any handlers attached to root get log messages from EVERYTHING,
    # like third-party modules, etc.
    'root': {
        'handlers': ["pg"],
        'level': 'DEBUG',
    },

    'version': 1,

    # This is important!  Without it, any log instances created before
    # you run logging.config.dictConfig(...) will be disabled, which
    # means all the global log objects in all the various imported files
    # won't do anything.
    'disable_existing_loggers': False,
})

def run_sql_commands(sql_text, user, password, host, database):

    """
    Run a whole bunch of SQL commands.  This is nice when you have a
    script with more than one statement in it.

    Don't pass me the path to a SQL script file!  Instead, give me the
    sql text after you read it in from a file.
    """

    env = os.environ.copy()
    env['PGPASSWORD'] = password

    # Feed the sql_text to psql's stdin.
    # http://stackoverflow.com/questions/163542/python-how-do-i-pass-a-string-into-subprocess-popen-using-the-stdin-argument
    p = subprocess.Popen([
        "psql",
        "--quiet",
        "--no-psqlrc",
        "-U",
        user,
        "-h",
        host,
        "-d",
        database,
        "--single-transaction",
        ],
        stdin=subprocess.PIPE,
        env=env)

    out = p.communicate(input=sql_text)

    return out
