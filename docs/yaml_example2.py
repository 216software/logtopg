# vim: set expandtab ts=4 sw=4 filetype=python:

import logging
import logging.config
import textwrap

import boto3
import yaml

def configure_logging():

    yaml_style_config = textwrap.dedent("""
    version: 1

    loggers:
        myscript: &myscriptlogging
            level: DEBUG
            handlers: [console, pg]

    handlers:
        console:
            class: logging.StreamHandler
            level: DEBUG
            formatter: colorfmt

        pg:
            class:          logtopg.PGHandler
            level:          DEBUG
            log_table_name: simvuly_logs
            database:       simvuly_matt
            host:           localhost
            user:           matt
            password:       m@tt1sc00l
            port:           5432

    formatters:

        colorfmt:
            (): "colorlog.ColoredFormatter"
            format: "%(log_color)s%(asctime)-22s [%(process)d] %(name)-30s %(lineno)-5d %(levelname)-8s %(message)s"

    """)

    d = yaml.safe_load(yaml_style_config)

    logging.config.dictConfig(d)

if __name__ == '__main__':

    configure_logging()

    logging.debug('This is a boring debug message.')
    logging.info('Here is an info message...')
    logging.warning('This is a warning message!')
    logging.error('Even worse, This is an error message!')
    logging.critical('OH NO THIS IS CRITICAL')

    # Now do something with boto3 and see all the logs it spits
    s3 = boto3.resource("s3")
    for bucket in s3.buckets.all():
        print(bucket.name)


    logging.info('All done!')
