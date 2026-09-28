# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

"""
The handler must survive its own connection dying: reconnect once and
retry, and if that fails too, hand the record to handleError rather
than raising out of the caller's log call.  No database needed.

    python -m pytest logtopg/tests/test_reconnect.py
"""

import logging
from unittest import mock

import psycopg2
import pytest

import logtopg


def make_handler(connections):

    """
    A PGHandler whose make_pgconn hands out the given fake connections
    in order, and whose table check is skipped.
    """

    h = logtopg.PGHandler("test_logs", database="x")
    h.log_table_exists = True
    h.connections = list(connections)

    def make_pgconn():
        h.pgconn = h.connections.pop(0)

    h.make_pgconn = make_pgconn
    return h


def make_conn(execute_error=None, cursor_error=None):
    conn = mock.Mock()
    if cursor_error:
        conn.cursor.side_effect = cursor_error
    if execute_error:
        conn.cursor.return_value.execute.side_effect = execute_error
    return conn


def make_record():
    return logging.LogRecord("test", logging.INFO, __file__, 1,
                             "hello", None, None)


def test_healthy_connection_inserts_once():
    conn = make_conn()
    h = make_handler([conn])
    h.emit(make_record())
    assert conn.cursor.return_value.execute.call_count == 1
    assert h.connections == []


def test_closed_connection_is_replaced_and_row_written():
    dead = make_conn(cursor_error=psycopg2.InterfaceError(
        "connection already closed"))
    fresh = make_conn()
    h = make_handler([dead, fresh])
    h.emit(make_record())
    assert h.pgconn is fresh
    assert fresh.cursor.return_value.execute.call_count == 1


def test_dropped_connection_is_replaced_and_row_written():
    dead = make_conn(execute_error=psycopg2.OperationalError(
        "server closed the connection unexpectedly"))
    fresh = make_conn()
    h = make_handler([dead, fresh])
    h.emit(make_record())
    assert h.pgconn is fresh
    assert fresh.cursor.return_value.execute.call_count == 1


def test_second_failure_goes_to_handle_error_not_raise():
    dead = make_conn(cursor_error=psycopg2.InterfaceError("closed"))
    still_dead = make_conn(execute_error=psycopg2.OperationalError("down"))
    h = make_handler([dead, still_dead])
    with mock.patch.object(h, "handleError") as handle_error:
        h.emit(make_record())
    handle_error.assert_called_once()


def test_reconnect_failure_goes_to_handle_error_not_raise():
    dead = make_conn(cursor_error=psycopg2.InterfaceError("closed"))
    h = make_handler([dead])

    def refuse():
        raise psycopg2.OperationalError("could not connect to server")

    h.make_pgconn = refuse
    with mock.patch.object(h, "handleError") as handle_error:
        h.emit(make_record())
    handle_error.assert_called_once()


def test_other_errors_go_to_handle_error_not_raise():
    conn = make_conn(execute_error=psycopg2.ProgrammingError("bad sql"))
    h = make_handler([conn])
    with mock.patch.object(h, "handleError") as handle_error:
        h.emit(make_record())
    handle_error.assert_called_once()
    assert h.pgconn is conn


def test_table_check_runs_once_per_handler():
    conn = make_conn()
    h = make_handler([conn])
    h.log_table_exists = False
    with mock.patch.object(h, "check_if_log_table_exists",
                           return_value=True) as check:
        h.emit(make_record())
        h.emit(make_record())
    assert check.call_count == 1
    assert h.log_table_exists is True


def test_emit_through_logging_does_not_take_caller_down():
    dead = make_conn(cursor_error=psycopg2.InterfaceError("closed"))
    still_dead = make_conn(execute_error=psycopg2.OperationalError("down"))
    h = make_handler([dead, still_dead])
    logger = logging.getLogger("logtopg.tests.reconnect")
    logger.addHandler(h)
    try:
        with mock.patch.object(h, "handleError"):
            logger.info("this must not raise")
    finally:
        logger.removeHandler(h)
