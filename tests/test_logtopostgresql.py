# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import logging
import logging.config
import os
import unittest

import logtopostgresql
import psycopg2

class Test1(unittest.TestCase):

    db_credentials = {
        "database":"logtopg",
        "host":"localhost",
        "user":"logtopg",
        "password":"l0gt0pg"}

    d = dict({

        'handlers': {
            'pg': {
                'class': 'logtopostgresql.PGHandler',
                'level': 'DEBUG',
                'logtablename': 'logtopg_tests',

                # These need to be correct, so you'll likely need to
                # change them.
                'params': db_credentials
            }},

        'root': {
            'handlers': ['pg'],
            'level': 'DEBUG'},

        'version': 1})

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
        Verify we make only one database connection in an instance.
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

        self.assertTrue(row[0], )

        # Subsequent calls to maybe_create_table should be harmless and
        # nearly instantaneous.
        ltpg.maybe_create_table()
        ltpg.maybe_create_table()
        ltpg.maybe_create_table()

        ltpg.pgconn.rollback()

    def test_4(self):

        """
        Verify log messages are stored in the database.
        """

        logging.config.dictConfig(self.d)

        log = logging.getLogger("logtopostgresql.tests")


        log.debug("debug!")
        log.info("info!")
        log.warn("warn!")
        log.error("error!")
        log.critical("critical!")

        # Now check that those logs are actually in the database.

        # Grab the pgconn off the handler.
        pgconn = log.root.handlers[0].pgconn

        cursor = pgconn.cursor()

        log_table_name = self.d["handlers"]["pg"]["logtablename"]

        cursor.execute(
            """
            select *
            from {}
            where process = %s
            """.format(log_table_name), [os.getpid()])

        # There should be 5 logs in the database with this process's ID.
        self.assertEqual(cursor.rowcount, 5)

        pgconn.rollback()

    def test_5(self):

        """
        Verify different logger instances use a single database
        connection.
        """

        logging.config.dictConfig(self.d)

        log1 = logging.getLogger("logtopostgresql.tests.a")
        log1.debug("trying this guy out")

        log2 = logging.getLogger("logtopostgresql.tests.b")
        log2.debug("trying this guy out")


def tearDownModule():

    # TODO: define all these credentials once and then reuse them.
    pgconn = psycopg2.connect(
        database=Test1.db_credentials["database"],
        host=Test1.db_credentials["host"],
        user=Test1.db_credentials["user"],
        password=Test1.db_credentials["password"]
    )

    cursor = pgconn.cursor()

    cursor.execute("drop table if exists logtopg_tests")

    pgconn.commit()


if __name__ == "__main__":
    unittest.main()
