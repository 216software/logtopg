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

    d = logtopg.example_dict_config
    log_table_name = d["handlers"]["pg"]["log_table_name"]
    db_credentials = d["handlers"]["pg"]["params"]


    def setUp(self):

        logging.config.dictConfig(self.d)

        self.log = logging.getLogger("logtopg.tests")

        self.ltpg = logtopg.PGHandler(
            self.log_table_name,
            self.db_credentials)

        # Make a separate database connection to check results in
        # database.
        self.test_pgconn = psycopg2.connect(**self.db_credentials)

    def test_1(self):

        """
        Verify we only read sql files once each.
        """

        self.assertTrue(self.ltpg.create_table_sql is None)

        s1 = self.ltpg.get_create_table_sql()

        self.assertTrue(isinstance(self.ltpg.create_table_sql, basestring))

        s2 = self.ltpg.get_create_table_sql()

        self.assertTrue(s1 is s2)

        self.ltpg.get_insert_row_sql()


    def test_2(self):

        """
        Verify we make only one database connection in an instance.
        """

        ltpg = logtopg.PGHandler(
            self.log_table_name,
            self.db_credentials)

        self.assertTrue(ltpg.pgconn is None)

        conn1 = ltpg.get_pgconn()

        self.assertTrue(ltpg.pgconn)

        conn2 = ltpg.get_pgconn()

        self.assertTrue(conn1 is conn2)


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

        log1 = logging.getLogger("logtopg.tests")
        log2 = logging.getLogger("logtopg.tests")
        log3 = logging.getLogger("logtopg.tests")
        log4 = logging.getLogger("logtopg.tests")

        log = logging.getLogger("logtopg.tests")

        log.debug("debug!")
        log.info("info!")
        log.warning("warning!")
        log.error("error!")
        log.critical("critical!")

        # Now check that those logs are actually in the database.
        pgconn = log.root.handlers[0].get_pgconn()
        cursor = pgconn.cursor()

        cursor.execute(
            """
            select message
            from {}
            where process = %s
            """.format(self.log_table_name), [os.getpid()])

        for row in cursor:
            print row[0]

        counted_rows = cursor.rowcount

        pgconn.rollback()

        # There should be 7 logs in the database with this process's ID.
        # Those 7 are the five above and the two connection logs.
        self.assertEqual(counted_rows, 7)


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

    def test_6(self):

        """
        Log an exception to the database.
        """

        logging.config.dictConfig(self.d)
        log = logging.getLogger("logtopg.tests.tests_6")

        try:

            1/0

        except Exception as ex:

            log.exception(ex)

        log.debug(AttributeError("This is a bogus exception"))

    def test_7(self):

        """
        Log something weird to the database, where "something weird"
        means something that can't be adapted.
        """

        logging.config.dictConfig(self.d)
        log = logging.getLogger("logtopg.tests.tests_7")

        class Unadaptable(object):
            pass

        u = Unadaptable()

        log.debug("u is a {0}.".format(u))
        log.debug(u)
        log.debug(dict(u=u))

    def tearDown(self):

        self.test_pgconn.rollback()

        cursor = self.test_pgconn.cursor()

        cursor.execute(
            "drop table if exists {0}".format(
                Test1.log_table_name))

        self.test_pgconn.commit()


def tearDownModule():

    pgconn = psycopg2.connect(**Test1.db_credentials)

    cursor = pgconn.cursor()

    cursor.execute(
        "drop table if exists {0}".format(
            Test1.log_table_name))

    pgconn.commit()


if __name__ == "__main__":
    unittest.main()
