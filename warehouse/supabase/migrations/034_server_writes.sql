-- Energy Research Warehouse (ERW): Supabase, migration 034 (session 301): the security review's H3 and M1
-- (docs/reviews/2026-10-10-security.md). The site's writes go server side with the service key since session 301
-- (site/lib/supabase.ts, writeConfig), so the anon key no longer needs to write anything: its four insert policies and
-- insert grants go, with its use of the four sequences (L6), and its right to execute site_ask_admit, whose counts a
-- holder of the anon key could otherwise fill with invented visitors. The service role is not bound by row-level
-- security and keeps every privilege through Supabase's default grants; site_ask_admit is granted to it by name.
--
-- Nothing a page reads changes: the game's leaderboard keeps its select policy (anon_read, migration 013), and no
-- table, column or row is touched. Order of the change: SUPABASE_SERVICE_KEY on the site's server first (Vercel and
-- site/.env.local), the site of session 301 second, this migration last; a site without the key would then fail to
-- store a play, a sign-up or a model call, so apply this only once the key is on the server.
--
-- Written in session 301 and NOT applied by it (a schema change is the owner's; a code machine writes no warehouse
-- data): python warehouse/supabase/apply.py --only 034. Rollback: ../rollbacks/034_server_writes.sql, applied with
-- apply.py --rollback 034 (it puts the policies, grants and the execute right back as migrations 005 to 023 made them).
-- Safe to run again.

-- H3: the model-call ledger (migration 010; migration 023 granted question_id)
drop policy if exists anon_insert on public.site_api_calls;
revoke insert on public.site_api_calls from anon, authenticated;
do $$ begin if to_regclass('public.site_api_calls_id_seq') is not null then revoke all on sequence public.site_api_calls_id_seq from anon, authenticated; end if; end $$;   -- an identity column's sequence (L6)

-- M1: the game's two tables (migrations 013 and 014)
drop policy if exists anon_insert on public.game_scores;
revoke insert on public.game_scores from anon, authenticated;
revoke all on sequence public.game_scores_id_seq from anon, authenticated;
drop policy if exists anon_insert on public.game_plays;
revoke insert on public.game_plays from anon, authenticated;
revoke all on sequence public.game_plays_id_seq from anon, authenticated;

-- M1: the subscribers (migrations 005 to 007)
drop policy if exists anon_insert on public.subscribers;
revoke insert on public.subscribers from anon, authenticated;
do $$ begin if to_regclass('public.subscribers_id_seq') is not null then revoke all on sequence public.subscribers_id_seq from anon, authenticated; end if; end $$;   -- an identity column's sequence (L6)

-- M1: the question counter (migration 023): the site calls it with the service key since session 301
revoke execute on function public.site_ask_admit(text, integer, numeric, numeric) from public, anon, authenticated;
grant execute on function public.site_ask_admit(text, integer, numeric, numeric) to service_role;
