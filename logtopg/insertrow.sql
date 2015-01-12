insert into {0} (
    created,
    name,
    loglevel,
    loglevelname,
    message,
    module,
    funcname,
    lineno,
    exception,
    process_id,
    process_name,
    thread,
    threadname
) values (
    to_timestamp(%(created)s),
    %(name)s,
    %(levelno)s,
    %(levelname)s,
    %(message)s,
    %(module)s,
    %(funcName)s,
    %(lineno)s,
    %(exc_text)s,
    %(process)s,
    %(process)s,
    %(thread)s,
    %(threadName)s
)

