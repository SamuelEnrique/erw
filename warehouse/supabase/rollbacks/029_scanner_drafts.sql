-- Energy Research Warehouse (ERW): the rollback of migration 029 (session 181). It lives in rollbacks/, not in
-- migrations/, so that apply.py's full run and its --only never pick it up; it is applied by name, by a person:
--
--     python warehouse/supabase/apply.py --rollback 029
--
-- It removes what 029 added: the three functions the site calls and the table public.scanner_drafts. THE DRAFTS AND
-- THEIR STATES (approved, dismissed, full card asked) ARE DELETED WITH THE TABLE; nothing else is touched. Each scan's
-- flags and drafts stay on the data machine under runs/scanner/<date>/, so a draft can be loaded again.
--
-- The site keeps working without them: /internal/findings says the review list cannot be read, /analysis draws no
-- scanner group, and a done request's card cannot be opened from the list (public.analysis_requests and its rows are
-- migration 027's and are not touched). Safe to run again.

drop function if exists public.analysis_request_card(text, text);
drop function if exists public.scanner_draft_set_state(text, text, text, text);
drop function if exists public.scanner_drafts_list(text, text, integer);
drop table if exists public.scanner_drafts;
