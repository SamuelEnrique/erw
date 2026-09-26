-- Energy Research Warehouse (ERW): Supabase live set, migration 001 (session 10).
--
-- The three table shapes of docs/datastandard.md, each with the standard columns
-- plus table_name (the ERW table a row belongs to) and license ('public' or
-- 'internal', from warehouse/metadata/coverage.csv). Columns that are not in the
-- standard (for example EIA-860M's eia_status, a queue's iso_status, a news
-- story's significance) are kept in `extra` (jsonb), so no table's own fields are
-- lost and the shapes stay fixed. loaded_at is the load run that last wrote a
-- row; after loading a table, load.py deletes that table's rows with an older
-- loaded_at, so a thing that left the source (a retired generator, a row older
-- than the 90-day window) leaves the live set too. Also: latest_prices (one row per entity and
-- variable, the newest real-time interval), catalogue (coverage.csv: one row per
-- ERW table) and sources (warehouse/metadata/sources.csv, for citations).
--
-- Supabase's free tier is capped at 500 MB; the live set must stay under 300 MB
-- (warehouse/supabase/load.py checks pg_database_size after every load).
-- Redivis is the store of record for every table; this database is derived from
-- the ERW tables and is rebuilt, never edited by hand.

create table if not exists public.series (
    table_name   text             not null,
    entity       text             not null,
    variable     text             not null,
    ts_utc       timestamptz      not null,
    value        double precision not null,
    unit         text             not null,
    freq         text,
    geo          text,
    market       text,
    node         text,
    source       text             not null,
    source_url   text,
    retrieved_at timestamptz,
    vintage      text,
    license      text             not null check (license in ('public', 'internal')),
    loaded_at    timestamptz      not null default now(),
    primary key (table_name, entity, variable, ts_utc)
);
create index if not exists series_ts on public.series (table_name, ts_utc);
create index if not exists series_entity on public.series (entity, variable, ts_utc);

create table if not exists public.entities (
    table_name   text             not null,
    entity_id    text             not null,
    entity_type  text             not null,
    name         text,
    geo          text,
    lat          double precision check (lat between -90 and 90),
    lon          double precision check (lon between -180 and 180),
    capacity_mw  double precision,
    status       text,
    status_date  date,
    operator     text,
    source       text             not null,
    source_url   text,
    retrieved_at timestamptz,
    vintage      text,
    extra        jsonb            not null default '{}'::jsonb,
    license      text             not null check (license in ('public', 'internal')),
    loaded_at    timestamptz      not null default now(),
    primary key (table_name, entity_id)
);
create index if not exists entities_geo on public.entities (table_name, geo);

create table if not exists public.events (
    table_name   text             not null,
    event_id     text             not null,
    event_date   timestamptz      not null,
    event_type   text             not null,
    parties      text,
    entity_ids   text,
    mw           double precision,
    price        double precision,
    currency     text,
    status       text,
    source       text             not null,
    source_url   text             not null,
    extra        jsonb            not null default '{}'::jsonb,
    license      text             not null check (license in ('public', 'internal')),
    loaded_at    timestamptz      not null default now(),
    primary key (table_name, event_id)
);
create index if not exists events_date on public.events (table_name, event_date desc);

-- The newest real-time price per hub or zone, refreshed every 15 minutes by
-- warehouse/connectors/latest_prices.py. No completeness rule: one row per
-- (entity, variable), replaced on each run.
create table if not exists public.latest_prices (
    entity       text             not null,
    variable     text             not null,
    ts_utc       timestamptz      not null,
    value        double precision not null,
    unit         text             not null,
    source       text             not null,
    retrieved_at timestamptz      not null,
    license      text             not null check (license in ('public', 'internal')),
    primary key (entity, variable)
);

-- One row per ERW table: warehouse/metadata/coverage.csv, loaded whole.
create table if not exists public.catalogue (
    table_name       text primary key,
    iso              text,
    market           text,
    n_nodes          bigint,
    interval         text,
    ts_min           timestamptz,
    ts_max           timestamptz,
    n_rows           bigint,
    source_report    text,
    last_run         timestamptz,
    validator_status text,
    license          text not null check (license in ('public', 'internal')),
    sector           text,
    derived          text,
    in_live_set      text not null default 'no'
);

-- The provenance header lines of every table in the live set (the '#' lines of its CSV),
-- so a reader of the live set sees where every number came from.
create table if not exists public.headers (
    table_name text    not null,
    line_no    integer not null,
    line       text    not null,
    license    text    not null check (license in ('public', 'internal')),
    primary key (table_name, line_no)
);

-- warehouse/metadata/sources.csv: the report behind every source id, for citations.
create table if not exists public.sources (
    source        text primary key,
    publisher     text,
    report        text,
    report_url    text,
    document_list text,
    license       text not null check (license in ('public', 'internal')),
    tables        text,
    first_seen    text,
    last_seen     text
);

-- Size of this database, for load.py's 300 MB guard. Callable by the service role only.
create or replace function public.erw_db_size() returns bigint
    language sql security definer set search_path = public
    as $$ select pg_database_size(current_database()) $$;
revoke all on function public.erw_db_size() from public, anon, authenticated;
grant execute on function public.erw_db_size() to service_role;
