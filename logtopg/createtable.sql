create table if not exists {0} (
    created text,
    name ltree,
    loglevel int,
    loglevelname text,
    message text,
    args text,
    module text,
    funcname text,
    lineno int,
    exception text,
    process int,
    thread text,
    threadname text,
    inserted timestamptz not null default now(),
    updated timestamptz
);
