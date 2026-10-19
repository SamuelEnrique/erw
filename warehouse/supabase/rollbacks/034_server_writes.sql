-- Energy Research Warehouse (ERW): the rollback of migration 034 (session 301). It lives in rollbacks/, not in
-- migrations/, so that apply.py's full run and its --only never pick it up; it is applied by name, by a person:
--
--     python warehouse/supabase/apply.py --rollback 034
--
-- It puts back what 034 removed: the anon key's insert policies and insert grants on the four tables, its use of the
-- game's two sequences (the two identity sequences were never granted by a migration: Supabase's default privileges
-- gave them, and 034's revoke is not undone here), and its right to execute site_ask_admit, each as the migration that
-- made it wrote it (005 to 007, 010, 013, 014, 023). No row is touched. Safe to run again.

-- the model-call ledger (010, 023)
drop policy if exists anon_insert on public.site_api_calls;
create policy anon_insert on public.site_api_calls for insert to anon with check (true);
grant insert (step, model, input_tokens, cached_input_tokens, cache_write_tokens, output_tokens, usd, request_id, question_id) on public.site_api_calls to anon;

-- the game's two tables (013, 014)
drop policy if exists anon_insert on public.game_scores;
create policy anon_insert on public.game_scores for insert to anon with check (true);
grant insert (level_date, nickname, score, optimal_score, "check", preset, difficulty) on public.game_scores to anon;
grant usage, select on sequence public.game_scores_id_seq to anon;
drop policy if exists anon_insert on public.game_plays;
create policy anon_insert on public.game_plays for insert to anon with check (true);
grant insert (session_id, level_date, actions, score, "check", preset, difficulty, settings) on public.game_plays to anon;
grant usage, select on sequence public.game_plays_id_seq to anon;

-- the subscribers (005 to 007)
drop policy if exists anon_insert on public.subscribers;
create policy anon_insert on public.subscribers for insert to anon with check (source = 'site');
grant insert (email, source, daily, weekly, topics) on public.subscribers to anon;

-- the question counter (023)
grant execute on function public.site_ask_admit(text, integer, numeric, numeric) to anon, authenticated;
