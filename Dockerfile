# vim: set expandtab ts=4 sw=4 filetype=docker fileencoding=utf8:

# Development/test postgresql server for the logtopg project.
#
# This container is only used by logtopg's own test suite and for local
# development.  People who use logtopg in their own projects supply
# their own postgresql server, so this image is not meant for them.
#
# Build and run:
#
#     docker build -t logtopg-postgres .
#     docker run --name logtopg-postgres -p 5433:5432 -d logtopg-postgres
#
# Then run logtopg's tests against it:
#
#     LOGTOPG_TEST_HOST=localhost \
#     LOGTOPG_TEST_PORT=5433 \
#     LOGTOPG_TEST_USER=logtopg \
#     LOGTOPG_TEST_PASSWORD=l0gt0pg \
#     LOGTOPG_TEST_DATABASE=logtopg_tests \
#     python setup.py test
#
# Stop and remove it with:
#
#     docker stop logtopg-postgres && docker rm logtopg-postgres

FROM postgres:16

# The logtopg tests connect as user "logtopg" to database
# "logtopg_tests".  These values mirror .travis.yml and the example
# config in logtopg/__init__.py.  The password is only ever used for
# local development and testing.
ENV POSTGRES_USER=logtopg
ENV POSTGRES_PASSWORD=l0gt0pg
ENV POSTGRES_DB=logtopg_tests

# logtopg's log table uses the ltree column type, and its create table
# script indexes cmd_line with pg_trgm.  The scripts in
# /docker-entrypoint-initdb.d are run once, when the data directory is
# first created, as POSTGRES_USER against the POSTGRES_DB database, so
# both extensions end up in logtopg_tests.
COPY docker/initdb/ /docker-entrypoint-initdb.d/

EXPOSE 5432
