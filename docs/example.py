# vim: set expandtab ts=4 sw=4 filetype=python fileencoding=utf8:

import logging
import logging.config

log = logging.getLogger("logtopg.example")

if __name__ == "__main__":

    # These need to be correct, so you'll likely need to change them.
    db_credentials = {
        "database":"logtopg",
        "host":"localhost",
        "user":"logtopg",
        "password":"l0gt0pg"}

    d = dict({
        'disable_existing_loggers': False,

        'handlers': {

            'pg': {
                'class': 'logtopg.PGHandler',
                'level': 'DEBUG',
                'log_table_name': 'logtopg_example',

                'params': db_credentials},

            "console": {
                "class": "logging.StreamHandler",
                "level": "DEBUG"
            }},

        'root': {
            'handlers': ["console", 'pg'],
            'level': 'DEBUG'},

        'version': 1})

    logging.config.dictConfig(d)

    log.debug("debug!")
    log.info("info!")
    log.warn("warn!")
    log.error("error!")
    log.critical("critical!")


