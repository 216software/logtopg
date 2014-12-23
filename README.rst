+++++++++++++++++
Log to PostgreSQL
+++++++++++++++++

.. image:: https://travis-ci.org/216software/logtopg.svg?branch=master
   :target: https://travis-ci.org/216software/logtopg


Install
=======

Grab the code with pip::

    $ pip install logtopg

But you also have to install the ltree contrib module into your
database::

    $ sudo -u postgres psql -c "create extension ltree;"

Try it out
==========

Here's an example script::

    import logging
    import logging.config

    log = logging.getLogger("logtopg.example")

    if __name__ == "__main__":

        # These need to be correct, so you'll likely need to change them.
        db_credentials = {
            "database":"logtopg",
            "host":"localhost",
            "user":"logtopg",
            "password":"l0gt0pg"}

        d = dict({
            'disable_existing_loggers': False,

            'handlers': {

                'pg': {
                    'class': 'logtopg.PGHandler',
                    'level': 'DEBUG',
                    'log_table_name': 'logtopg_example',

                    'params': db_credentials},

                "console": {
                    "class": "logging.StreamHandler",
                    "level": "DEBUG"
                }},

            'root': {
                'handlers': ["console", 'pg'],
                'level': 'DEBUG'},

            'version': 1})

        logging.config.dictConfig(d)

        log.debug("debug!")
        log.info("info!")
        log.warn("warn!")
        log.error("error!")
        log.critical("critical!")


Contribute to logtopg
=====================

Get a copy of the code::

    $ git clone --origin github https://github.com/216software/logtopg.git

Install it like this::

    $ cd logtopg
    $ pip install -e .

Create test user and test database::

    $ sudo -u postgres createuser --pwprompt logtopg
    $ sudo -u postgres createdb --owner logtopg logtopg
    $ sudo -u postgres psql -c "create extension ltree;"

Then run the tests like this::

    $ python setup.py --quiet test
    .....
    ----------------------------------------------------------------------
    Ran 5 tests in 0.379s

    OK

Hopefully it works!


Stuff to do
===========

*   Look if there are any other columns we could store.  Can we look up
    process names for a process ID and store the name?

*   Add indexes on columns that are likely to be used in where-clauses,
    such as:

        *   log name (the ltree column)
        *   process ID
        *   inserted
        *   log level (DEBUG, INFO, WARN, ERROR, CRITICAL)

*   Add a trigger to set the updated column if a row is ever updated.

*   Write some documentation showing how to use the ltree column type to
    get logs just for a part of an application.

*   Do some load-testing with tons of connected processes and tons of
    logging messages.  Make sure that logging doesn't compete with real
    application work for database resources.  Is there a way to say,
    "Hey postgresql, take your time with this stuff, and deal with other
    stuff first!"


.. vim: set syntax=rst:
