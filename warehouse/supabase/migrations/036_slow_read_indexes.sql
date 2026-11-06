-- Energy Research Warehouse (ERW): Supabase live set, migration 036 (session 580). Written, not applied: applying it is
-- Samuel's or the data machine's (python warehouse/supabase/apply.py --only 036), after reading
-- docs/reviews/slow-reads-2026-10-22.md. Its rollback is rollbacks/036_slow_read_indexes.sql.
--
-- Session 580 timed every read of a build and of a route check against it (lib/supabase.ts with ERW_READ_TIMING=1).
-- Of the five slowest requests, two kinds are answered by an index that does not fit them:
--
--   1. The map and the resources overlay read the interconnection queue's projects out of energy_projects
--      (entities, table_name 'energy_projects', extra->>'kind' = 'queue', in entity_id order, a thousand rows a
--      page). 3,713 of the table's 34,634 rows are queue rows. The primary key (table_name, entity_id) gives the order
--      but not the filter: each page walks about nine rows for each one it keeps, and the page at offset 3000 walks
--      most of the table (about 190 ms alone on 22 October, 6.9 s in a build's opening burst).
--   2. The nine event pages read event_window_daily by event (series, table_name 'event_window_daily', event =
--      '<event>', in the key's order). The event is the last column of the primary key (table_name, entity,
--      variable, ts_utc, event), so a read of one event (1,515 rows of the table's 29,953 for cold_2026) walks every
--      row of the table and keeps one in twenty (5.3 s in the build's opening burst).
--
-- Both indexes are partial, one table each, as migration 032's is: about 3,700 and 30,000 entries, small beside the
-- 300 MB the live set must stay under. Each holds the read's filter first and its order after, so a page is one
-- range of the index. The planner can use a partial index only when the query names the table as a literal, which a
-- PostgREST filter does; whether it does is to be confirmed with EXPLAIN in the SQL editor once applied (PostgREST
-- refuses a plan to the anon key: PGRST107, 22 October). No page's query changes. Idempotent.

create index if not exists entities_projects_kind
  on public.entities ((extra ->> 'kind'), entity_id)
  where table_name = 'energy_projects';

create index if not exists series_event_window_by_event
  on public.series (event, entity, variable, ts_utc)
  where table_name = 'event_window_daily';

analyze public.entities;
analyze public.series;
