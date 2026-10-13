-- Energy Research Warehouse (ERW): Supabase, migration 031 (session 233): the weekly hunt's drafts in the review list.
-- docs/methods/automated_analysis_findings.md, "The weekly hunt".
--
-- The weekly hunt (warehouse/analysis/findings/hunt.py) writes its drafts where the scanner writes its own, so that
-- one page (/internal/findings) holds everything that waits for a ruling. Three changes to migration 029's table:
--
--   rule    the check gains 'hunt' beside the scanner's five rules
--   files   a new column (jsonb, default {}): a draft's files by name, each {kind: text | png, content}: the CSV, the
--           Stata do-file, the Python mirror, the two LinkedIn pictures (1200 x 627 and 1080 x 1080, base64) and the
--           caption. The list function of 029 names its columns and does not return this one, so the page's list
--           stays as light as it was; a file is fetched one at a time
--   scanner_draft_file(p_token, p_id, p_name)   one file of one draft, behind the internal token as 029's functions
--           are. It reads and never writes. A draft or a name that is not there answers null
--
-- Internal as before: row-level security on, no policy, no privilege for public, anon or authenticated. Nothing here
-- makes a draft public: a draft reaches /analysis only when a person approves it at /internal/findings.
--
-- Safe to run again: the constraint is dropped and added, the column is added if absent, the function is replaced.
-- Rollback: ../rollbacks/031_hunt_drafts.sql, applied with apply.py --rollback 031 (it deletes the hunt's drafts).

alter table public.scanner_drafts drop constraint if exists scanner_drafts_rule_check;
alter table public.scanner_drafts add constraint scanner_drafts_rule_check
  check (rule in ('record', 'negative', 'spike', 'weekly', 'pair', 'hunt'));
alter table public.scanner_drafts add column if not exists files jsonb not null default '{}'::jsonb;

create or replace function public.scanner_draft_file(p_token text, p_id text, p_name text)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
begin
  if not erw_private.site_token_ok(p_token) then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  if p_id is null or p_id !~ '^scan-[a-z]+-[0-9a-f]{12}$' or p_name is null or p_name !~ '^[A-Za-z0-9_.-]{3,120}$' then
    return null;
  end if;
  return (
    select jsonb_build_object('id', d.id, 'name', p_name, 'state', d.state, 'kind', d.files -> p_name ->> 'kind',
                              'content', d.files -> p_name ->> 'content')
    from public.scanner_drafts d where d.id = p_id and d.files ? p_name);
end;
$$;
revoke all on function public.scanner_draft_file(text, text, text) from public;
grant execute on function public.scanner_draft_file(text, text, text) to anon, authenticated;
