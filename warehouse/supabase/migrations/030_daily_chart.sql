-- Energy Research Warehouse (ERW): Supabase, migration 030 (session 232): the Digest's daily chart, its candidates.
-- docs/methods/automated_analysis_scanner.md, "The daily chart in the Digest".
--
-- One internal table, public.daily_chart_candidates: one row a UTC day, written by the data machine after each daily
-- scan (warehouse/analysis/findings/daily_chart.py, publish) and read by the runner when it writes the weekday Digest
-- (warehouse/news/brief.py). The histories the scanner compares with are on the data machine only; the Digest is
-- written on GitHub's runner. This table is how the day's ranked flags, each with the finding card computed for it by
-- code, and the watch list's changes of the latest period cross from one to the other.
--
--   day              the scan's date (UTC); a later scan of the same day replaces the row
--   computed_at      when the candidates were computed
--   machine          the data machine's name
--   scanner_version  the scanner's version (warehouse/config/scanner.yaml)
--   candidates       [{source: scanner | watch, key, rank, fact, table, series_key, flag (scanner), card}], ranked
--
-- Internal means what it means for migration 029's table: row-level security is on, no policy exists, and every
-- privilege of public, anon and authenticated is revoked, so the site's public key reads and writes nothing in it. It
-- is in no live set and no Redivis dataset, and no page of the site reads it. Both machines reach it with the service
-- role, which bypasses row-level security. No function is added.
--
-- Safe to run again: the table is created if absent. Nothing existing is changed.
-- Rollback: ../rollbacks/030_daily_chart.sql, applied with apply.py --rollback 030 (it drops the table; each day's
-- candidates stay on the data machine under runs/scanner/<date>/daily_chart.json).

create table if not exists public.daily_chart_candidates (
  day             date primary key,
  computed_at     timestamptz not null default now(),
  machine         text not null default '',
  scanner_version text not null default '',
  candidates      jsonb not null default '[]'::jsonb
);
alter table public.daily_chart_candidates enable row level security;
revoke all on public.daily_chart_candidates from public, anon, authenticated;
