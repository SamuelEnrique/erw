-- Energy Research Warehouse (ERW): the rollback of migration 030 (session 232). It lives in rollbacks/, not in
-- migrations/, so that apply.py's full run and its --only never pick it up; it is applied by name, by a person:
--
--     python warehouse/supabase/apply.py --rollback 030
--
-- It removes what 030 added: the table public.daily_chart_candidates, with the days it holds. Nothing else is touched.
-- Each day's candidates stay on the data machine under runs/scanner/<date>/daily_chart.json, and the next daily scan
-- writes the day's row again once the table is back.
--
-- The Digest keeps working without the table: it finds no candidates, tries the watch list on the runner's own tables,
-- and leaves the section out with the reason logged when that gives nothing. Safe to run again.

drop table if exists public.daily_chart_candidates;
