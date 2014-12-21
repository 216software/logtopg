# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import psycopg2
import logging
import textwrap
import time

# Ganked from http://stackoverflow.com/questions/20354321/is-this-postgresql-logging-handler-correct

log = logging.getLogger("logtopostgresql")

class psqlHandler(logging.Handler):

    initial_sql = textwrap.dedent("""
        CREATE TABLE IF NOT EXISTS log(
            Created text,
            Name text,
            LogLevel int,
            LogLevelName text,
            Message text,
            Args text,
            Module text,
            FuncName text,
            LineNo int,
            Exception text,
            Process int,
            Thread text,
            ThreadName text
        )
        """)

    insertion_sql = textwrap.dedent("""
        INSERT INTO log(
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
        try:
            self.__connect = psycopg2.connect(
                database=self.__database,
                host = self.__host,
                user = self.__user,
                password = self.__password,
                sslmode="disable")

            return True
        except:
            return False

    def __init__(self, params):

        if not params:
            raise Exception ("No database where to log ☻")

        self.__database = params['database']
        self.__host = params['host']
        self.__user = params['user']
        self.__password = params['password']

        self.__connect = None

        if not self.connect():
            raise Exception ("Database connection error, no logging ☻")

        logging.Handler.__init__(self)

        self.__connect.cursor().execute(psqlHandler.initial_sql)
        self.__connect.commit()
        self.__connect.cursor().close()

        log.info("Just ran the SQL to create a table.")


    def emit(self, record):

        # Use default formatting:
        self.format(record)

        if record.exc_info:
            record.exc_text = logging._defaultFormatter.formatException(record.exc_info)
        else:
            record.exc_text = ""

        # Insert log record:
        try:
            cur = self.__connect.cursor()
        except:
            self.connect()
            cur = self.__connect.cursor()

        cur.execute(psqlHandler.insertion_sql, record.__dict__)

        self.__connect.commit()
        self.__connect.cursor().close()

if __name__ == "__main__":

    myh = psqlHandler({'host':"localhost", 'user':"test",
                       'password':"testpw", 'database':"test"})

    l = logging.getLogger("TEST")
    l.setLevel(logging.DEBUG)
    l.addHandler(myh)


    for i in xrange(1):
        l.info("test%i"%i)
