-- Energy Research Warehouse (ERW), session 135: Thesis Builder as a tool of the site (/thesis, in review).
--
-- One internal table, public.thesis_runs: a row per run a person asked for on /thesis, with the report the server wrote
-- and the PitchBook stage's request and answer. Internal means: row level security is on, no policy exists, and every
-- grant to anon and authenticated is revoked, so the site's public key reads and writes nothing in it. The table is in
-- no live set, no Redivis dataset and no download route. The server-side builder (warehouse/thesis/run.py) writes
-- it with the service role, which bypasses row level security.
--
-- The site reaches it only through four functions:
--   1. thesis_submit(p_token, p_niche, p_stage, p_geography): a run is queued and the workflow thesis.yml dispatched
--      through public.erw_dispatch (migration 015: the database's own GitHub token, in Vault). Behind the internal
--      token, as internal_ask_spend is (erw_private.settings, internal_costs_token). At most p_per_day runs are
--      queued in a UTC day, counted here, so a held-down button cannot spend without limit.
--   2. thesis_list(p_token): the runs, newest first, without their reports.
--   3. thesis_get(p_token, p_run_id): one run with its report, its PitchBook request (and one-time key while unused)
--      and the PitchBook answer.
--   4. thesis_pitchbook_accept(p_run_id, p_key, p_payload): the PitchBook stage's answer, accepted once under the
--      run's one-time key. No internal token: the key is the credential, it is 43 characters of randomness, it opens
--      one write to one run, and it is erased when used. The site's route validates and labels the payload before it
--      calls this; the function checks the key, the size and the outer shape again.
--
-- Nothing here holds a prompt, a research plan or a scoring rule: the report is what a reader of /thesis sees.
--
-- Idempotent: the table is created if absent, the functions are replaced.

create table if not exists public.thesis_runs (
  run_id                 text primary key,
  requested_at           timestamptz not null default now(),
  niche                  text not null,
  stage                  text not null default '',
  geography              text not null default '',
  status                 text not null default 'queued' check (status in ('queued', 'running', 'done', 'failed')),
  note                   text not null default '',          -- a failed run's plain reason; never a stack trace
  started_at             timestamptz,
  finished_at            timestamptz,
  usd                    numeric,                            -- the run's model spend, for the owner
  report                 jsonb,                              -- the report as /thesis draws it
  pitchbook_request      jsonb,                              -- the lookups asked of PitchBook
  pitchbook_key          text,                               -- one-time; null once used
  pitchbook              jsonb,                              -- PitchBook's figures as returned, every one labeled
  pitchbook_received_at  timestamptz
);
alter table public.thesis_runs enable row level security;
revoke all on public.thesis_runs from public, anon, authenticated;
create index if not exists thesis_runs_requested on public.thesis_runs (requested_at desc);

create or replace function public.thesis_token_ok(p_token text)
returns boolean language plpgsql stable security definer set search_path = '' as $$
declare
  secret text;
begin
  select value into secret from erw_private.settings where key = 'internal_costs_token';
  return secret is not null and length(secret) >= 24 and p_token is not null and p_token = secret;
end;
$$;
revoke all on function public.thesis_token_ok(text) from public, anon, authenticated;

create or replace function public.thesis_submit(p_token text, p_niche text, p_stage text, p_geography text, p_per_day integer default 6)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare
  niche text := btrim(regexp_replace(coalesce(p_niche, ''), '\s+', ' ', 'g'));
  stage text := btrim(regexp_replace(coalesce(p_stage, ''), '\s+', ' ', 'g'));
  geo   text := btrim(regexp_replace(coalesce(p_geography, ''), '\s+', ' ', 'g'));
  today date := (now() at time zone 'utc')::date;
  n     integer;
  id    text;
  sent  boolean := false;
begin
  if not public.thesis_token_ok(p_token) then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  if length(niche) < 8 or length(niche) > 400 or length(stage) > 80 or length(geo) > 80 then
    return jsonb_build_object('ok', false, 'reason', 'input');
  end if;
  select count(*) into n from public.thesis_runs where (requested_at at time zone 'utc')::date = today;
  if n >= greatest(1, least(coalesce(p_per_day, 6), 24)) then
    return jsonb_build_object('ok', false, 'reason', 'day', 'runs_today', n);
  end if;
  id := to_char(now() at time zone 'utc', 'YYYYMMDD"T"HH24MISS"Z"') || '-' || substr(md5(random()::text || clock_timestamp()::text), 1, 6);
  insert into public.thesis_runs (run_id, niche, stage, geography) values (id, niche, stage, geo);
  begin
    perform public.erw_dispatch('thesis.yml', jsonb_build_object('ref', 'main', 'inputs', jsonb_build_object('run_id', id)));
    sent := true;
  exception when others then
    sent := false;      -- the run stays queued; the workflow's own schedule or a person's dispatch picks it up
  end;
  return jsonb_build_object('ok', true, 'run_id', id, 'dispatched', sent);
end;
$$;
revoke all on function public.thesis_submit(text, text, text, text, integer) from public;
grant execute on function public.thesis_submit(text, text, text, text, integer) to anon, authenticated;

create or replace function public.thesis_list(p_token text)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
begin
  if not public.thesis_token_ok(p_token) then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  return coalesce((
    select jsonb_agg(r order by r.requested_at desc)
    from (
      select run_id, niche, stage, geography, status, note, requested_at, started_at, finished_at,
             coalesce(jsonb_array_length(report -> 'landscape' -> 'companies'), 0) as companies,
             case when pitchbook is not null then 'received' when pitchbook_request is not null then 'pending' else 'none' end as pitchbook
      from public.thesis_runs order by requested_at desc limit 200
    ) r), '[]'::jsonb);
end;
$$;
revoke all on function public.thesis_list(text) from public;
grant execute on function public.thesis_list(text) to anon, authenticated;

create or replace function public.thesis_get(p_token text, p_run_id text)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare
  r public.thesis_runs%rowtype;
begin
  if not public.thesis_token_ok(p_token) then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  select * into r from public.thesis_runs where run_id = p_run_id;
  if not found then
    return null;
  end if;
  return jsonb_build_object(
    'run_id', r.run_id, 'niche', r.niche, 'stage', r.stage, 'geography', r.geography, 'status', r.status, 'note', r.note,
    'requested_at', r.requested_at, 'started_at', r.started_at, 'finished_at', r.finished_at,
    'report', r.report, 'pitchbook_request', r.pitchbook_request, 'pitchbook_key', r.pitchbook_key,
    'pitchbook', r.pitchbook, 'pitchbook_received_at', r.pitchbook_received_at);
end;
$$;
revoke all on function public.thesis_get(text, text) from public;
grant execute on function public.thesis_get(text, text) to anon, authenticated;

create or replace function public.thesis_pitchbook_accept(p_run_id text, p_key text, p_payload jsonb)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare
  r public.thesis_runs%rowtype;
begin
  if p_key is null or length(p_key) < 32 or p_run_id is null then
    return jsonb_build_object('ok', false, 'reason', 'key');
  end if;
  select * into r from public.thesis_runs where run_id = p_run_id for update;
  if not found or r.pitchbook_key is null or r.pitchbook_key <> p_key then
    return jsonb_build_object('ok', false, 'reason', 'key');      -- unknown run, wrong key and used key answer alike
  end if;
  -- "is distinct from": a payload with no company list gives a null type, and null <> 'array' is null, not true
  if p_payload is null or jsonb_typeof(p_payload) is distinct from 'object' or jsonb_typeof(p_payload -> 'companies') is distinct from 'array'
     or jsonb_array_length(p_payload -> 'companies') > 300 or length(p_payload::text) > 400000 then
    return jsonb_build_object('ok', false, 'reason', 'shape');
  end if;
  update public.thesis_runs
     set pitchbook = p_payload, pitchbook_received_at = now(), pitchbook_key = null
   where run_id = p_run_id;
  return jsonb_build_object('ok', true, 'companies', jsonb_array_length(p_payload -> 'companies'));
end;
$$;
revoke all on function public.thesis_pitchbook_accept(text, text, jsonb) from public;
grant execute on function public.thesis_pitchbook_accept(text, text, jsonb) to anon, authenticated;
