# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import os
import subprocess

def run_sql_script(sql_text, user, password, host, database):

    """
    Run a SQL script via psql.  This is nice when you have a script with
    more than one statement in it.

    Give me the sql text after you read it in from a file or whatever.
    """

    env = os.environ.copy()
    env['PGPASSWORD'] = password

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
