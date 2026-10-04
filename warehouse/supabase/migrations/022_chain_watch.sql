-- Energy Research Warehouse (ERW): Supabase, migration 022 (session 91).
--
-- The chain watch in the database's schedule (migration 015): every 15 minutes pg_cron dispatches
-- .github/workflows/chain-watch.yml, which emails one line when a chain of unattended sessions marked as running
-- (scripts/alert.py chain start) has saved nothing for 30 minutes. docs/machines.md, "Alerts".
--
-- Apply it only once chain-watch.yml is on main: a dispatch of a workflow main does not hold is refused by GitHub
-- (HTTP 404) every 15 minutes. GitHub's own schedule in the workflow file starts it too, late and not every time; the
-- workflow skips the duplicate.
--
-- Apply this one alone: python warehouse/supabase/apply.py --only 022

do $$
begin
  if exists (select 1 from cron.job where jobname = 'erw-chain-watch') then
    perform cron.unschedule('erw-chain-watch');
  end if;
end $$;
select cron.schedule('erw-chain-watch', '*/15 * * * *',
  $$select public.erw_dispatch('chain-watch.yml')$$);
