create table if not exists {0} (

    created timestamptz,

    process_id int,
    process_name text,

    logger_name ltree,

    path_name text,
    module text,
    file_name text,

    function_name text,

    line_number int,

    log_level text,

    message text,

    log_level_number int,

    exc_info text,
    thread_id integer,
    threadname text,
    inserted timestamptz not null default now()
);

create index on {0} (created);
create index on {0} (inserted);
create index on {0} (logger_name);
create index on {0} (process_id);
