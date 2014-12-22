# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import logging
import logging.config
import unittest

import logtopostgresql

class Test1(unittest.TestCase):

    def test_1(self):

        """
        Verify we only read sql files once each.
        """

        ltpg = logtopostgresql.PGHandler(
            "boguslogs",

            # You need to set these to whatever your test database
            # is.  Read the README for example code on setting up a
            # database.
            dict(
                database="logtopg",
                host="localhost",
                user="logtopg",
                password="l0gt0pg"))

        self.assertIsNone(ltpg.create_table_sql)

        s1 = ltpg.get_create_table_sql()

        self.assertIsInstance(ltpg.create_table_sql, str)

        s2 = ltpg.get_create_table_sql()

        self.assertIs(s1, s2)

        ltpg.get_insert_row_sql()


    def test_2(self):

        """
        Verify we make only one database connection.
        """

        ltpg = logtopostgresql.PGHandler(
            "boguslogs",

            # You will need to set these to whatever your test database
            # is
            dict(
                database="logtopg",
                host="localhost",
                user="logtopg",
                password="l0gt0pg"))

        self.assertIsNone(ltpg.pgconn)

        conn1 = ltpg.get_pgconn()

        self.assertTrue(ltpg.pgconn)

        conn2 = ltpg.get_pgconn()

        self.assertIs(conn1, conn2)


    def test_3(self):

        """
        Verify we can create the log table.
        """

        ltpg = logtopostgresql.PGHandler(
            "test_3_log_table",

            # You will need to set these to whatever your test database
            # is
            dict(
                database="logtopg",
                host="localhost",
                user="logtopg",
                password="l0gt0pg"))

        ltpg.maybe_create_table()

        # Now, verify the table exists.
        cursor = ltpg.pgconn.cursor()

        cursor.execute("""
            select exists(
                select *
                from information_schema.tables
                where table_name = %s)
            """, ["test_3_log_table"])

        row = cursor.fetchone()

        self.assertTrue(row[0])

        # Subsequent calls to maybe_create_table should be harmless and
        # nearly instantaneous.
        ltpg.maybe_create_table()
        ltpg.maybe_create_table()
        ltpg.maybe_create_table()

    def test_4(self):

        """
        Verify log messages are stored in the database.
        """

        # First, set up logging.
        d = dict({
            'formatters': {
                'consolefmt': {
                    'format': '%(asctime)s %(levelname)-10s %(process)-6d %(filename)-24s %(lineno)-4d %(message)s'}},

            'handlers': {
                'pg': {
                    'class': 'logtopostgresql.PGHandler',
                    'level': 'DEBUG',
                    'formatter': 'consolefmt',
                    'logtablename': 'test_4_logs',

                    'params': dict(
                        database="logtopg",
                        host="localhost",
                        user="logtopg",
                        password="l0gt0pg")
                }},

            'root': {
                'handlers': ['pg'],
                'level': 'DEBUG'},

            'version': 1})

        logging.config.dictConfig(d)

        log = logging.getLogger("logtopg.tests")

        log.debug("debug!")


if __name__ == "__main__":
    unittest.main()
