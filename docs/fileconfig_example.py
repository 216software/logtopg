# vim: set expandtab ts=4 sw=4 filetype=python:

import logging
import logging.config

if __name__ == '__main__':

    logging.config.fileConfig("simple_example.cfg")

    logging.debug('This is a boring debug message.')
    logging.info('Here is an info message...')
    logging.warning('This is a warning message!')
    logging.error('Even worse, This is an error message!')
    logging.critical('OH NO THIS IS CRITICAL')

    logging.info('All done!')
