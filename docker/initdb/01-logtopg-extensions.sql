-- Extensions that logtopg's log table needs.

-- The ltree type is used for the logger_name column in logtopg's log
-- table.  logtopg does not create this extension itself.
CREATE EXTENSION IF NOT EXISTS ltree;

-- logtopg's create table script uses this for the cmd_line GIN index.
CREATE EXTENSION IF NOT EXISTS pg_trgm;
