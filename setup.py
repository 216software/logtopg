# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

from setuptools import setup

setup(
    name="LogToPG",
    version="0.0.2",
    packages=["logtopg"],
    author="216 Software, LLC",
    author_email="info@216software.com",
    license="BSD License",
    include_package_data=True,

    install_requires=[
        'psycopg2',
    ]
)
