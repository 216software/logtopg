insert into {} (
    created,
    name,
    loglevel,
    loglevelname,
    message,
    module,
    funcname,
    lineno,
    exception,
    process,
    thread,
    threadname
) values (
    %(created)s,
    %(name)s,
    %(levelno)s,
    %(levelname)s,
    %(msg)s,
    %(module)s,
    %(funcName)s,
    %(lineno)s,
    %(exc_text)s,
    %(process)s,
    %(thread)s,
    %(threadName)s
)

