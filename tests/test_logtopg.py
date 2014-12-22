# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import logging
import logging.config
import os
import unittest

import logtopg
import psycopg2

class Test1(unittest.TestCase):

    """
    This depends on a real postgresql database.  I'll create a table and
    then drop it.
    """

    db_credentials = {
        "database":"logtopg",
        "host":"localhost",
        "user":"logtopg",
        "password":"l0gt0pg"}

    d = dict({

        'handlers': {
            'pg': {
                'class': 'logtopg.PGHandler',
                'level': 'DEBUG',
                'log_table_name': 'logtopg_tests',

                # These need to be correct, so you'll likely need to
                # change them.
                'params': db_credentials
            }},

        'root': {
            'handlers': ['pg'],
            'level': 'DEBUG'},

        'version': 1})

    log_table_name = d["handlers"]["pg"]["log_table_name"]

    def test_1(self):

        """
        Verify we only read sql files once each.
        """

        ltpg = logtopg.PGHandler(
            self.log_table_name,
            self.db_credentials)

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

        ltpg = logtopg.PGHandler(
            self.log_table_name,
            self.db_credentials)

        self.assertIsNone(ltpg.pgconn)

        conn1 = ltpg.get_pgconn()

        self.assertTrue(ltpg.pgconn)

        conn2 = ltpg.get_pgconn()

        self.assertIs(conn1, conn2)


    def test_3(self):

        """
        Verify we can create the log table.
        """

        ltpg = logtopg.PGHandler(
            self.log_table_name,
            self.db_credentials)

        ltpg.maybe_create_table()

        # Now, verify the table exists.
        cursor = ltpg.pgconn.cursor()

        cursor.execute("""
            select exists(
                select *
                from information_schema.tables
                where table_name = %s)
            """, [self.log_table_name])

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

        log = logging.getLogger("logtopg.tests")

        log.debug("debug!")
        log.info("info!")
        log.warn("warn!")
        log.error("error!")
        log.critical("critical!")

        # Now check that those logs are actually in the database.

        # Grab the pgconn off the handler.
        pgconn = log.root.handlers[0].pgconn

        cursor = pgconn.cursor()


        cursor.execute(
            """
            select *
            from {}
            where process = %s
            """.format(self.log_table_name), [os.getpid()])

        # There should be 5 logs in the database with this process's ID.
        self.assertEqual(cursor.rowcount, 5)

        pgconn.rollback()


    def test_5(self):

        """
        Verify different logger instances use a single database
        connection.
        """

        logging.config.dictConfig(self.d)

        log1 = logging.getLogger("logtopg.tests.a")
        log1.debug("trying this guy out")

        log2 = logging.getLogger("logtopg.tests.b")
        log2.debug("trying this guy out")


def tearDownModule():

    pgconn = psycopg2.connect(**Test1.db_credentials)

    cursor = pgconn.cursor()

    cursor.execute(
        "drop table if exists {}".format(
            Test1.log_table_name))

    pgconn.commit()


if __name__ == "__main__":
    unittest.main()
