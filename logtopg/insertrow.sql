insert into {0} (
    created,
    process_id,
    process_name,
    logger_name,
    path_name,
    module,
    file_name,
    function_name,
    line_number,
    log_level,
    log_level_number,
    message,
    exc_info,
    thread_id,
    thread_name
) values (
    to_timestamp(%(created)s),
    %(process)s,
    %(processName)s,
    %(name)s,
    %(pathname)s,
    %(module)s,
    %(filename)s,
    %(funcName)s,
    %(lineno)s,
    %(levelname)s,
    %(levelno)s,
    %(message)s,
    %(exc_text)s,
    %(thread)s,
    %(threadName)s
);

