# vim: set expandtab ts=4 sw=4 filetype=python:

import logging
import logging.config
import textwrap

import boto3
import yaml

log = logging.getLogger("mycode")

def configure_logging():

    yaml_style_config = textwrap.dedent("""
    version: 1

    disable_existing_loggers: false

    root:
        level: WARNING
        handlers: [console]

    loggers:

        mycode: &mycodelogging
            propagate: False
            level: DEBUG
            handlers: [console]

        botocore:
            propagate: False
            level: DEBUG
            handlers: [console]

    handlers:
        console:
            class: logging.StreamHandler
            level: DEBUG
            formatter: colorfmt

    formatters:

        colorfmt:
            (): "colorlog.ColoredFormatter"
            format: "%(log_color)s%(asctime)-22s [%(process)d] %(name)-30s %(lineno)-5d %(levelname)-8s %(message)s"

    """)

    d = yaml.safe_load(yaml_style_config)

    logging.config.dictConfig(d)

if __name__ == '__main__':

    configure_logging()

    log.debug('This is a boring debug message.')
    log.info('Here is an info message...')
    log.warning('This is a warning message!')
    log.error('Even worse, This is an error message!')
    log.critical('OH NO THIS IS CRITICAL')

    # Now do something with boto3 and see all the logs it spits
    session = boto3.Session(profile_name="matt-backups")
    s3 = session.client("s3")

    print("Here are the buckets I found:")

    for b in s3.list_buckets()["Buckets"]:
        print(b["Name"])

    log.info('All done!')
