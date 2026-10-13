-- Energy Research Warehouse (ERW): the rollback of migration 031 (session 233). It lives in rollbacks/, not in
-- migrations/, so that apply.py's full run and its --only never pick it up; it is applied by name, by a person:
--
--     python warehouse/supabase/apply.py --rollback 031
--
-- It removes what 031 added: the function public.scanner_draft_file, the column files of public.scanner_drafts, and
-- the rule 'hunt' from the table's check. THE WEEKLY HUNT'S DRAFTS (rule 'hunt') AND THEIR STATES ARE DELETED, because
-- the check of 029 would refuse them; the scanner's drafts are not touched. Every hunt's drafts and files stay on the
-- data machine under runs/hunt/<date>/, so they can be loaded again after 031 is applied again.
--
-- The site keeps working: /internal/findings lists the scanner's drafts as before and a hunt draft's file links
-- answer 404. Safe to run again.

drop function if exists public.scanner_draft_file(text, text, text);
delete from public.scanner_drafts where rule = 'hunt';
alter table public.scanner_drafts drop column if exists files;
alter table public.scanner_drafts drop constraint if exists scanner_drafts_rule_check;
alter table public.scanner_drafts add constraint scanner_drafts_rule_check
  check (rule in ('record', 'negative', 'spike', 'weekly', 'pair'));
