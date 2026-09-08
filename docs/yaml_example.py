# vim: set expandtab ts=4 sw=4 filetype=python:

import logging
import logging.config
import textwrap

import yaml

def configure_logging():

    yaml_style_config = textwrap.dedent("""
    version: 1

    root:
        level: INFO
        handlers: [console, tmpfile, pg, email]

    handlers:
        console:
            class: logging.StreamHandler
            level: DEBUG
            formatter: colorfmt

        tmpfile:
            class: logging.handlers.RotatingFileHandler
            filename: /tmp/clepy_logtopg_demo.log
            mode: a
            level: DEBUG
            formatter: consolefmt
            maxBytes: 1000000000
            backupCount: 7

        pg:
            class:          logtopg.PGHandler
            level:          DEBUG
            log_table_name: clepy_logtopg_demo_logs
            database:       clepy_logtopg_demo
            host:           null
            user:           matt
            password:       null
            port:           5432

        email:
            level: CRITICAL
            formatter: consolefmt
            class: logging.handlers.SMTPHandler
            mailhost: localhost

            fromaddr: matt@simvuly.com

            toaddrs:
                - matt@216software.com

            subject: production error (matt)

    formatters:
        consolefmt:
            format: '%(asctime)s %(levelname)-10s %(process)-6d %(filename)-24s %(lineno)-4d %(message)s'

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

    logging.info('All done!')
