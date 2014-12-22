# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

from setuptools import setup

setup(
    name="LogToPG",
    version="0.0.4",
    description="Python logging handler that stores logs in postgresql",
    url="https://github.com/216software/logtopg/",
    packages=["logtopg"],
    author="216 Software, LLC",
    author_email="info@216software.com",
    license="BSD License",
    include_package_data=True,

    install_requires=[
        'psycopg2',
    ]
)
