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

The code in `docs/example.py`_ shows how to set up your logging configs
with this handler.

.. _`docs/example.py`: https://github.com/216software/logtopg/blob/master/docs/example.py

.. include:: docs/example.py
    :number-lines:
    :code: python


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

*   Figure out how to discover when something can't be adapted, and then
    store a string version of it instead.

*   Replace all the text columns with data types that better match the
    underlying data.

*   Fill out classifiers in setup.py.

*   Look if there are any other columns we could store.  Can we look up
    process names for a process ID and store the name?

*   Add indexes on columns that are likely to be used in where-clauses,
    such as:

        *   log name (the ltree column)
        *   process ID
        *   inserted
        *   log level (DEBUG, INFO, WARN, ERROR, CRITICAL)

*   Add a trigger to set the updated column if a row is ever updated.

*   Create a few views of typical queries.

*   Test performance with many connected processes and tons of logging
    messages.  Make sure that logging doesn't compete with real
    application work for database resources.  Is there a way to say
    something like

        "Hey postgresql, take your time with this stuff, and deal with
        other stuff first!"

    In other words, a "nice" command for queries.

*   Allow people to easily write their own SQL to create the logging
    table and to insert records to it.  The queries could be returned
    from properties, so people would just need to subclass the PGHandler
    and then redefine those properties.

*   Write some documentation:

    *   installation
    *   typical queries
    *   tweak log table columns or indexes
    *   discuss performance issues

*   Set up a readthedocs page for logtopg for that documentation.

.. vim: set syntax=rst:
