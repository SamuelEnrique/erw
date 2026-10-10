-- Energy Research Warehouse (ERW): Supabase, migration 028 (session 177): the security audit's fixes that live in the
-- database, and the usage counts. docs/reviews/2026-10-10-security.md; docs/methods/usage_counts.md.
--
-- Three parts. Nothing here changes what a page reads: no existing policy, grant or row is dropped or rewritten.
--
--  A. Row-level security, asserted. Every table in schema public must have row-level security on; the eight tables the
--     site and the erw package read with the anon key must have their select policy and privilege; the internal
--     tables must have neither. When session 177 read the catalog all of this already held (runs/session177/
--     catalog.json), so on that database part A changes nothing and takes no lock: each statement runs only where the
--     state is not already the wanted one. It is here so that the rule is in a migration and not in a convention, and
--     so that a database rebuilt from the migrations ends in the same state. warehouse/supabase/verify_rls.py proves
--     the result with the anon key.
--
--  B. Rate limits that hold across the site's server instances. site_rate_counts holds, per limit ("bucket"), per
--     window of time and per visitor, a count; site_rate_admit adds one and answers whether the count is within the
--     limit the caller names. The visitor is a keyed hash the site's server makes from the address, the UTC day and a
--     secret the database never sees (site/lib/guard.ts, as site_ask_admit's visitor is, migration 023): no address
--     is stored, and the hash is another value the next day. Rows a day old are deleted by the next call.
--
--  C. Usage counts with no cookie and no personal data (/api/usage, /internal/usage).
--       site_usage_events   today only: day, path, tool, event, visitor (a hash, below), n
--       site_usage_daily    every earlier day, as counts only: day, path, tool, event, events, visitors. No hash.
--       site_usage_salt     one row: today's random salt. Deleted when its day is over.
--     The visitor of a row. The site's server sends a keyed hash of the address and the user agent (HMAC-SHA256 under
--     a secret only the server holds; the database never sees an address or a user agent). The database hashes that
--     again under a salt it draws at random for the UTC day (32 bytes of gen_random_bytes) and stores the first 32
--     hexadecimal characters. When the day is over (the first call of any function of parts B or C after 00:00 UTC),
--     the day's rows are added up into site_usage_daily as counts, the rows with their hashes are deleted, and the
--     salt is deleted. The salt is derived from nothing: it is random, so once its row is deleted it cannot be
--     computed again from anything this database or the site keeps. What is kept of an earlier day is counts.
--     (One honest limit: Supabase's own backups of this database, kept for their retention period, hold a copy of
--     whatever a table held when the backup ran.)
--
-- Who may call. Every function of B and C checks p_token against the secret the internal view's functions use
-- (erw_private.settings, internal_costs_token, written by apply.py from INTERNAL_COSTS_TOKEN): only the site's server
-- holds it. The anon key alone can execute the functions and gets "not authorized"; it can read and write none of the
-- four tables. So a person holding only the anon key cannot fill the counts or the limits.
--
-- Days are UTC days. Safe to run again: tables are created if absent, functions are replaced, part A is conditional.
-- Rollback: ../rollbacks/028_security_usage.sql, applied with apply.py --rollback 028 (it drops what parts B and C
-- add, with their counts; part A is never undone).

-- ---------------------------------------------------------------------------------------------------------------------
-- A. Row-level security, asserted
-- ---------------------------------------------------------------------------------------------------------------------
do $$
declare
  t record;
  licensed text[] := array['series', 'entities', 'events', 'latest_prices', 'catalogue', 'sources', 'headers'];
  internal text[] := array['game_plays', 'subscribers', 'email_suppressions', 'digest_sends', 'site_api_calls',
                           'site_ask_counts', 'erw_health', 'erw_locks', 'thesis_runs', 'thesis_provider_results',
                           'analysis_requests'];
  n text;
begin
  -- every table of schema public: row-level security on (only where it is off: no lock is taken on a table that has it)
  for t in select c.relname from pg_catalog.pg_class c join pg_catalog.pg_namespace s on s.oid = c.relnamespace
           where s.nspname = 'public' and c.relkind in ('r', 'p') and not c.relrowsecurity loop
    execute format('alter table public.%I enable row level security', t.relname);
    raise notice 'row-level security enabled on public.%', t.relname;
  end loop;
  -- the live set's shapes: the anon key reads rows whose license is public, and nothing else (migration 002)
  foreach n in array licensed loop
    if to_regclass('public.' || n) is null then continue; end if;
    if not exists (select 1 from pg_catalog.pg_policies p where p.schemaname = 'public' and p.tablename = n
                   and p.cmd = 'SELECT' and p.roles && array['anon']::name[]) then
      execute format('create policy public_rows on public.%I for select to anon, authenticated using (license = ''public'')', n);
      raise notice 'select policy created on public.%', n;
    end if;
    if not has_table_privilege('anon', 'public.' || n, 'select') then
      execute format('grant select on public.%I to anon, authenticated', n);
      raise notice 'select granted on public.%', n;
    end if;
  end loop;
  -- the game's leaderboard (migration 013): the anon key reads every row
  if to_regclass('public.game_scores') is not null
     and not exists (select 1 from pg_catalog.pg_policies p where p.schemaname = 'public' and p.tablename = 'game_scores'
                     and p.cmd = 'SELECT' and p.roles && array['anon']::name[]) then
    create policy anon_read on public.game_scores for select to anon using (true);
    raise notice 'select policy created on public.game_scores';
  end if;
  -- the internal tables: no select privilege for the anon key or a signed-in user (only where one is held)
  foreach n in array internal loop
    if to_regclass('public.' || n) is null then continue; end if;
    if has_table_privilege('anon', 'public.' || n, 'select') or has_table_privilege('authenticated', 'public.' || n, 'select') then
      execute format('revoke select on public.%I from anon, authenticated', n);
      raise notice 'select revoked on public.%', n;
    end if;
  end loop;
end $$;

-- ---------------------------------------------------------------------------------------------------------------------
-- B and C: the tables
-- ---------------------------------------------------------------------------------------------------------------------
create table if not exists public.site_rate_counts (
  bucket  text        not null check (bucket ~ '^[a-z][a-z0-9_]{2,31}$'),
  win     timestamptz not null,
  visitor text        not null check (visitor ~ '^[0-9a-f]{32}$'),
  n       integer     not null default 0 check (n >= 0),
  primary key (bucket, win, visitor)
);
create index if not exists site_rate_counts_win on public.site_rate_counts (win);
alter table public.site_rate_counts enable row level security;
revoke all on public.site_rate_counts from public, anon, authenticated;

create table if not exists public.site_usage_events (
  day     date    not null,
  path    text    not null check (path ~ '^/[A-Za-z0-9/_.~:%-]{0,119}$'),
  tool    text    not null default '' check (length(tool) <= 80 and tool !~ '[*[:cntrl:]]'),
  event   text    not null check (event in ('tool opened', 'input changed', 'scenario compared', 'download')),
  visitor text    not null check (visitor ~ '^[0-9a-f]{32}$'),
  n       integer not null default 1 check (n >= 1),
  primary key (day, path, tool, event, visitor)
);
create index if not exists site_usage_events_visitor on public.site_usage_events (day, visitor);
alter table public.site_usage_events enable row level security;
revoke all on public.site_usage_events from public, anon, authenticated;

-- counts only. A line of '*' in path, tool or event is a total over that column (so a day's distinct visitors, a
-- page's and a tool's are kept as numbers, which cannot be added up from the finer lines).
create table if not exists public.site_usage_daily (
  day      date    not null,
  path     text    not null,
  tool     text    not null,
  event    text    not null,
  events   bigint  not null check (events >= 0),
  visitors integer not null check (visitors >= 0),
  primary key (day, path, tool, event)
);
alter table public.site_usage_daily enable row level security;
revoke all on public.site_usage_daily from public, anon, authenticated;

create table if not exists public.site_usage_salt (
  day  date  primary key,
  salt bytea not null check (octet_length(salt) = 32)
);
alter table public.site_usage_salt enable row level security;
revoke all on public.site_usage_salt from public, anon, authenticated;

-- ---------------------------------------------------------------------------------------------------------------------
-- The functions
-- ---------------------------------------------------------------------------------------------------------------------

-- Is this the site's server? The same secret as the internal view's functions (migration 010). Never granted to anon.
create or replace function erw_private.site_token_ok(p_token text)
returns boolean language plpgsql stable security definer set search_path = '' as $$
declare
  secret text;
begin
  select value into secret from erw_private.settings where key = 'internal_costs_token';
  return secret is not null and length(secret) >= 24 and p_token is not null and p_token = secret;
end $$;
revoke all on function erw_private.site_token_ok(text) from public, anon, authenticated;

-- The counts of a day, at the four grains site_usage_daily keeps, from the rows that still hold their hashes.
create or replace function erw_private.usage_counts(p_from date, p_to date)
returns table (day date, path text, tool text, event text, events bigint, visitors integer)
language sql stable security definer set search_path = '' as $$
  select e.day, coalesce(e.path, '*'), coalesce(e.tool, '*'), coalesce(e.event, '*'), sum(e.n)::bigint, count(distinct e.visitor)::integer
  from (select u.day, u.path, u.tool, u.event, u.visitor, u.n from public.site_usage_events u where u.day >= p_from and u.day <= p_to) e
  group by grouping sets ((e.day, e.path, e.tool, e.event), (e.day, e.path), (e.day, e.tool), (e.day))
$$;
revoke all on function erw_private.usage_counts(date, date) from public, anon, authenticated;

-- The end of a day: earlier days' rows become counts, their hashes and their salt are deleted. Called by every
-- function below, so the first request of any kind after 00:00 UTC closes the day before.
create or replace function erw_private.usage_rollover()
returns void language plpgsql volatile security definer set search_path = '' as $$
declare
  today date := (now() at time zone 'utc')::date;
begin
  if exists (select 1 from public.site_usage_events where day < today) then
    perform pg_catalog.pg_advisory_xact_lock(1770177);    -- one closing at a time; the second finds nothing left
    insert into public.site_usage_daily (day, path, tool, event, events, visitors)
      select c.day, c.path, c.tool, c.event, c.events, c.visitors from erw_private.usage_counts('-infinity'::date, today - 1) c
      on conflict (day, path, tool, event) do update set events = excluded.events, visitors = excluded.visitors;
    delete from public.site_usage_events where day < today;
  end if;
  delete from public.site_usage_salt where day < today;
  delete from public.site_usage_daily where day < today - 730;    -- two years of counts are kept
end $$;
revoke all on function erw_private.usage_rollover() from public, anon, authenticated;

-- One request against one limit. Answers {ok, n}: n is the count in the current window, this request included.
create or replace function public.site_rate_admit(p_token text, p_bucket text, p_visitor text, p_limit integer, p_window_s integer)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare
  w timestamptz;
  seen integer;
begin
  if not erw_private.site_token_ok(p_token) then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  if p_bucket is null or p_bucket !~ '^[a-z][a-z0-9_]{2,31}$' or p_visitor is null or p_visitor !~ '^[0-9a-f]{32}$'
     or p_limit is null or p_limit < 0 or p_limit > 1000000 or p_window_s is null or p_window_s < 10 or p_window_s > 86400 then
    return jsonb_build_object('ok', false, 'reason', 'config');
  end if;
  perform erw_private.usage_rollover();
  delete from public.site_rate_counts where win < now() - interval '1 day';   -- a count a day old is deleted
  w := to_timestamp(floor(extract(epoch from now()) / p_window_s) * p_window_s);
  insert into public.site_rate_counts (bucket, win, visitor, n) values (p_bucket, w, p_visitor, 1)
    on conflict (bucket, win, visitor) do update set n = public.site_rate_counts.n + 1
    returning n into seen;
  return jsonb_build_object('ok', seen <= p_limit, 'reason', case when seen <= p_limit then null else 'limit' end, 'n', seen,
                            'retry_after', greatest(1, ceil(extract(epoch from (w + make_interval(secs => p_window_s) - now())))::integer));
end $$;
revoke all on function public.site_rate_admit(text, text, text, integer, integer) from public;
grant execute on function public.site_rate_admit(text, text, text, integer, integer) to anon, authenticated;

-- One usage event. p_visitor is the server's keyed hash of address and user agent (64 hexadecimal characters); what is
-- stored is that hash hashed again under today's random salt. At most 400 lines a visitor a day and 200,000 lines a
-- day are kept: beyond either the event is dropped and the answer says so.
create or replace function public.site_usage_record(p_token text, p_path text, p_tool text, p_event text, p_visitor text)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare
  today date := (now() at time zone 'utc')::date;
  s bytea;
  v text;
  mine integer;
begin
  if not erw_private.site_token_ok(p_token) then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  if p_path is null or p_path !~ '^/[A-Za-z0-9/_.~:%-]{0,119}$' or p_tool is null or length(p_tool) > 80 or p_tool ~ '[*[:cntrl:]]'
     or p_event is null or p_event not in ('tool opened', 'input changed', 'scenario compared', 'download')
     or p_visitor is null or p_visitor !~ '^[0-9a-f]{64}$' then
    return jsonb_build_object('ok', false, 'reason', 'input');
  end if;
  perform erw_private.usage_rollover();
  insert into public.site_usage_salt (day, salt) values (today, extensions.gen_random_bytes(32)) on conflict (day) do nothing;
  select salt into s from public.site_usage_salt where day = today;
  v := substr(encode(extensions.hmac(decode(p_visitor, 'hex'), s, 'sha256'), 'hex'), 1, 32);
  select count(*) into mine from public.site_usage_events where day = today and visitor = v;
  if mine >= 400 then
    update public.site_usage_events set n = n + 1 where day = today and path = p_path and tool = p_tool and event = p_event and visitor = v;
    if not found then
      return jsonb_build_object('ok', false, 'reason', 'visitor');
    end if;
    return jsonb_build_object('ok', true, 'reason', null);
  end if;
  if (select count(*) from public.site_usage_events where day = today) >= 200000 then
    return jsonb_build_object('ok', false, 'reason', 'busy');
  end if;
  insert into public.site_usage_events (day, path, tool, event, visitor, n) values (today, p_path, p_tool, p_event, v, 1)
    on conflict (day, path, tool, event, visitor) do update set n = public.site_usage_events.n + 1;
  return jsonb_build_object('ok', true, 'reason', null);
end $$;
revoke all on function public.site_usage_record(text, text, text, text, text) from public;
grant execute on function public.site_usage_record(text, text, text, text, text) to anon, authenticated;

-- The counts, for /internal/usage: the last p_days days (at most 400), today included. Counts only: no hash leaves.
create or replace function public.internal_usage(p_token text, p_days integer default 62)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare
  today date := (now() at time zone 'utc')::date;
  since date;
begin
  if not erw_private.site_token_ok(p_token) then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  since := today - least(greatest(coalesce(p_days, 62), 1), 400);
  perform erw_private.usage_rollover();
  return jsonb_build_object(
    'today', today,
    'since', since,
    'rows', coalesce((
      select jsonb_agg(jsonb_build_object('day', r.day, 'path', r.path, 'tool', r.tool, 'event', r.event, 'events', r.events, 'visitors', r.visitors)
                       order by r.day desc, r.events desc, r.path, r.tool, r.event)
      from (
        select d.day, d.path, d.tool, d.event, d.events, d.visitors from public.site_usage_daily d where d.day >= since
        union all
        select c.day, c.path, c.tool, c.event, c.events, c.visitors from erw_private.usage_counts(today, today) c
      ) r), '[]'::jsonb)
  );
end $$;
revoke all on function public.internal_usage(text, integer) from public;
grant execute on function public.internal_usage(text, integer) to anon, authenticated;
