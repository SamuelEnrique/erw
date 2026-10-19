-- Energy Research Warehouse (ERW): the rollback of migration 033 (session 289). It lives in rollbacks/, not in
-- migrations/, so that apply.py's full run and its --only never pick it up; it is applied by name, by a person:
--
--     python warehouse/supabase/apply.py --rollback 033
--
-- It puts back migration 019's check (v4 and before). A v5 row already stored fails the check, so delete or keep the
-- v5 rows first; no row is deleted here. Safe to run again.
alter table public.game_scores drop constraint if exists game_scores_preset_check;
alter table public.game_scores add constraint game_scores_preset_check check (preset ~ '^(easy|normal|hard):[0-9.]+-[0-9.]+-[0-9]+(-r[0-9]+-d[0-9.]+)?(-v3|(-[a-z]+)*-v4)?$');
alter table public.game_plays drop constraint if exists game_plays_preset_check;
alter table public.game_plays add constraint game_plays_preset_check check (preset ~ '^(easy|normal|hard):[0-9.]+-[0-9.]+-[0-9]+(-r[0-9]+-d[0-9.]+)?(-v3|(-[a-z]+)*-v4)?$');
