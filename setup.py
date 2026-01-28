# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import sys

if sys.version_info < (2, 7):
    raise Exception("sorry, this needs at least python 2.7!")

# Read __version__ from version.py
with open("logtopg/version.py") as f:
    exec(f.read())

from setuptools import find_packages, setup

setup(
    # name="LogToPG",
    name="logtopg",
    version=__version__,
    description="Python logging handler that stores logs in postgresql",
    url="https://github.com/216software/logtopg/",
    packages=find_packages(),

    author="216 Software, LLC",
    author_email="info@216software.com",
    license="BSD License",
    include_package_data=True,

    install_requires=[
        'psycopg2',
    ],

    # Are these not allowed any more?
    # test_suite="nose.collector",
    # use_2to3=True,
)
