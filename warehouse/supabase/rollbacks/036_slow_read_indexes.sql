-- Energy Research Warehouse (ERW): the rollback of migration 036 (session 580). It lives in rollbacks/, not in
-- migrations/, so that apply.py's full run and its --only never pick it up; it is applied by name, by a person:
--
--     python warehouse/supabase/apply.py --rollback 036
--
-- It drops the two partial indexes of migration 036. No row is deleted. The queue read of energy_projects and the
-- event pages' reads of event_window_daily go back to the primary keys. Safe to run again.

drop index if exists public.entities_projects_kind;
drop index if exists public.series_event_window_by_event;
