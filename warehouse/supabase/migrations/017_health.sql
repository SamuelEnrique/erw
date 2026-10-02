-- Energy Research Warehouse (ERW), session 61: the health record of scheduled jobs (warehouse/health.py).
-- One row per scheduled step: ok, skipped (it should not have run: the data lock held, the day's work done, nothing new
-- at the source), retried (failed once, then passed) or failed (failed twice). The daily job writes the previous UTC
-- day's rows into queue/summary/<day>-health.md; a job never fails on GitHub for these, so GitHub never emails.
-- Service key only: row-level security on, no policy, nothing granted to anon or authenticated.

create table if not exists public.erw_health (
  id bigserial primary key,
  at timestamptz not null default now(),
  workflow text not null,
  run_id text,
  step text not null,
  status text not null check (status in ('ok', 'skipped', 'retried', 'failed')),
  reason text,
  seconds numeric
);
create index if not exists erw_health_at on public.erw_health (at);
alter table public.erw_health enable row level security;
revoke all on public.erw_health from anon, authenticated;
revoke all on sequence public.erw_health_id_seq from anon, authenticated;
