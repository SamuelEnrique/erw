-- Energy Research Warehouse (ERW): the rollback of migration 028 (session 177). It lives in rollbacks/, not in
-- migrations/, so that apply.py's full run and its --only never pick it up; it is applied by name, by a person:
--
--     python warehouse/supabase/apply.py --rollback 028
--
-- It removes what parts B and C of 028 added: the three functions the site calls, the three private helpers and the
-- four tables. THE USAGE COUNTS AND THE RATE-LIMIT COUNTS ARE DELETED WITH THEIR TABLES; nothing else is touched.
-- Part A of 028 (row-level security asserted) is never undone: on the database session 177 read it changed nothing.
--
-- The site keeps working without them: the rate limits fall back to each server instance's memory (site/lib/guard.ts),
-- /api/usage records nothing, and /internal/usage says the counts cannot be read. Safe to run again.

drop function if exists public.internal_usage(text, integer);
drop function if exists public.site_usage_record(text, text, text, text, text);
drop function if exists public.site_rate_admit(text, text, text, integer, integer);
drop function if exists erw_private.usage_rollover();
drop function if exists erw_private.usage_counts(date, date);
drop function if exists erw_private.site_token_ok(text);
drop table if exists public.site_usage_salt;
drop table if exists public.site_usage_daily;
drop table if exists public.site_usage_events;
drop table if exists public.site_rate_counts;
