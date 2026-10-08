-- Energy Research Warehouse (ERW), session 150: Thesis Builder (/thesis, in review), the data providers of the fetch
-- stage. Beside PitchBook (migration 024) a run may now hold an answer of Harmonic and of Crunchbase, each pasted by a
-- person from a Claude chat that holds the provider's connector under their own account.
--
-- WHAT THIS MIGRATION DOES NOT TOUCH. public.thesis_runs is not altered: no column is added, no row is read, written
-- or rewritten, and none of the functions of migration 024 is replaced (thesis_submit, thesis_list, thesis_get,
-- thesis_pitchbook_accept stay exactly as they are). The pending PitchBook request of run 20261006T193517Z-50a8be and
-- its one-time key are therefore as they were. A record on thesis_runs names no provider: it is PitchBook's, and is
-- read so in code (site/lib/thesis/providers.ts, providerOf; warehouse/thesis/providers.py, provider_of).
--
-- One new internal table, public.thesis_provider_results: at most one row a run and provider.
--   harmonic, crunchbase   the answer as the site's reader wrote it out (labeled, with what was not mapped kept as
--                          given), the time it was pasted and the SHA-256 of the pasted text
--   pitchbook              the time and the SHA-256 of the pasted text only (payload null): PitchBook's answer itself
--                          stays on the run's own row, stored by thesis_pitchbook_accept as before
-- Internal as thesis_runs is: row level security on, no policy, every grant to anon and authenticated revoked. The
-- table is in no live set, no Redivis dataset and no download route. A row goes when its run goes.
--
-- The site reaches it through two functions, both behind the internal token (thesis_token_ok, migration 024): the
-- paste box is on the internal page, so the browser's internal cookie is the credential and no key travels in the
-- request text of the two new providers.
--   1. thesis_provider_accept(p_token, p_run_id, p_provider, p_format, p_sha256, p_payload): a provider's answer for
--      a finished run, accepted once (a second answer of the same provider for the same run is refused, not merged).
--   2. thesis_provider_results(p_token, p_run_id): the rows of one run.
--
-- Idempotent: the table is created if absent, the functions are replaced.

create table if not exists public.thesis_provider_results (
  run_id         text not null references public.thesis_runs (run_id) on delete cascade,
  provider       text not null check (provider in ('pitchbook', 'harmonic', 'crunchbase')),
  format         text not null check (format in ('erw-pitchbook-1', 'erw-harmonic-1', 'erw-crunchbase-1')),
  pasted_at      timestamptz not null default now(),
  pasted_sha256  text not null check (pasted_sha256 ~ '^[0-9a-f]{64}$'),      -- of the pasted text, as pasted
  payload        jsonb,                                                        -- null for pitchbook: its answer is on thesis_runs
  primary key (run_id, provider)
);
alter table public.thesis_provider_results enable row level security;
revoke all on public.thesis_provider_results from public, anon, authenticated;

create or replace function public.thesis_provider_accept(p_token text, p_run_id text, p_provider text, p_format text, p_sha256 text, p_payload jsonb)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare
  r      public.thesis_runs%rowtype;
  want   text;
begin
  if not public.thesis_token_ok(p_token) then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  want := case p_provider when 'pitchbook' then 'erw-pitchbook-1' when 'harmonic' then 'erw-harmonic-1' when 'crunchbase' then 'erw-crunchbase-1' else null end;
  if want is null or p_format is distinct from want or p_sha256 is null or p_sha256 !~ '^[0-9a-f]{64}$' then
    return jsonb_build_object('ok', false, 'reason', 'shape');
  end if;
  select * into r from public.thesis_runs where run_id = p_run_id;      -- read only: the run's row is never written here
  if not found or r.status <> 'done' then
    return jsonb_build_object('ok', false, 'reason', 'run');
  end if;
  if p_provider = 'pitchbook' then
    -- only the stamp of an answer the run already holds: the answer itself was stored by thesis_pitchbook_accept
    if r.pitchbook is null or p_payload is not null then
      return jsonb_build_object('ok', false, 'reason', 'shape');
    end if;
  else
    -- "is distinct from": a payload with no company list gives a null type, and null <> 'array' is null, not true
    if p_payload is null or jsonb_typeof(p_payload) is distinct from 'object' or jsonb_typeof(p_payload -> 'companies') is distinct from 'array'
       or jsonb_array_length(p_payload -> 'companies') > 300 or length(p_payload::text) > 400000
       or (p_payload ->> 'format') is distinct from want or (p_payload ->> 'run_id') is distinct from p_run_id then
      return jsonb_build_object('ok', false, 'reason', 'shape');
    end if;
  end if;
  insert into public.thesis_provider_results (run_id, provider, format, pasted_sha256, payload)
  values (p_run_id, p_provider, want, p_sha256, p_payload)
  on conflict (run_id, provider) do nothing;
  if not found then
    return jsonb_build_object('ok', false, 'reason', 'held');             -- one answer a provider and run
  end if;
  return jsonb_build_object('ok', true, 'companies', coalesce(jsonb_array_length(p_payload -> 'companies'), 0));
end;
$$;
revoke all on function public.thesis_provider_accept(text, text, text, text, text, jsonb) from public;
grant execute on function public.thesis_provider_accept(text, text, text, text, text, jsonb) to anon, authenticated;

create or replace function public.thesis_provider_results(p_token text, p_run_id text)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
begin
  if not public.thesis_token_ok(p_token) then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  return coalesce((
    select jsonb_agg(jsonb_build_object('provider', provider, 'format', format, 'pasted_at', pasted_at, 'pasted_sha256', pasted_sha256, 'payload', payload) order by pasted_at)
    from public.thesis_provider_results where run_id = p_run_id), '[]'::jsonb);
end;
$$;
revoke all on function public.thesis_provider_results(text, text) from public;
grant execute on function public.thesis_provider_results(text, text) to anon, authenticated;
