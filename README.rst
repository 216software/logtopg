+++++++++++++++++
Log to PostgreSQL
+++++++++++++++++

.. image:: https://travis-ci.org/216software/logtopg.svg?branch=master
    :target: https://travis-ci.org/216software/logtopg

.. image:: https://circleci.com/gh/216software/logtopg.png?circle-token=389fee16249541b4b1df6e8a7f8edb1401be66de
   :target:https://circleci.com/gh/216software/logtopg

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

*   Fill out classifiers in setup.py.

*   Somehow block updates to the table.  Maybe a trigger is the right
    way.  Maybe there's a much simpler trick that I'm not aware of.

*   Create a few views for typical queries.

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

*   Experiment with what happens when the emit(...) function call takes
    a long time.  For example, say somebody is logging to a PG server
    across the internet, will calls to log.debug(...) slow down  the
    local app?  I imagine so.

*   I just found out that the ltree column type (that I use for logger
    names) can not handle logger names like "dazzle.insert-stuff".  That
    dash in there is invalid syntax.

    I hope there is a way to raise an exception as soon as somebody uses
    an invalid logger name.

    Or, maybe I need to convert the invalid name to a valid name, by
    maybe substituting any of a set of characters with something else.


.. vim: set syntax=rst:
