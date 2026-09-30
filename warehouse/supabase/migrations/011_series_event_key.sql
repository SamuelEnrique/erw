-- Energy Research Warehouse (ERW): Supabase live set, migration 011 (session 36C).
--
-- event_window_daily (docs/methods/events.md) holds the days around several events, and an event's days or baseline
-- days may be another event's days: its key is (entity, variable, ts_utc, event) (docs/datastandard.md, decision 32).
-- The series table gets the event column, '' for every other table, and its primary key includes it. Idempotent: the
-- key is rebuilt only while it does not yet hold event.

alter table public.series add column if not exists event text not null default '';

do $$
begin
  if not exists (
    select 1 from information_schema.key_column_usage
    where table_schema = 'public' and table_name = 'series' and constraint_name = 'series_pkey' and column_name = 'event'
  ) then
    alter table public.series drop constraint if exists series_pkey;
    alter table public.series add constraint series_pkey primary key (table_name, entity, variable, ts_utc, event);
  end if;
end $$;
