create table if not exists {0} (

    log_id int generated
    by default as identity primary key,

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
    log_level_number int,

    cmd_line text,

    message text,

    exc_info text,
    thread_id bigint,
    thread_name text,
    inserted timestamptz not null default now()
);

create index on {0} (created);
create index on {0} (inserted);
create index on {0} (logger_name);
create index on {0} (process_id);

CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE INDEX idx_{0}_cmdline ON {0} USING GIN (cmd_line gin_trgm_ops);
