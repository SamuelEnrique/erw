-- Energy Research Warehouse (ERW), session 170: Automated Analysis findings, the queue (/analysis, in review).
--
-- One internal table, public.analysis_requests: a row per request a person makes on /analysis, of two kinds:
--   run       a finding with chosen inputs (finding, params). The data machine's worker (warehouse/analysis/findings/
--             worker.py) takes queued rows in order when it is awake, runs the finding against the full histories it
--             holds, and writes the card into the row (card jsonb, card_id) with status done or failed. When the
--             machine is off the row stays queued: /analysis shows it with the time it was asked, and the worker takes
--             it when the machine wakes.
--   roundup   the finding chosen for the Sunday Roundup of a week (params: card_id, week). warehouse/news/roundup.py
--             reads the latest one for its week with the service role; none chosen, it falls back to the rule's chart
--             of the week and says so.
-- Internal means: row level security is on, no policy exists, and every grant to anon and authenticated is revoked, so
-- the site's public key reads and writes nothing in it. The table is in no live set and no Redivis dataset. The site
-- reaches it through two functions behind the internal token (erw_private.settings, internal_costs_token, as the
-- Thesis Builder's are, migration 024): analysis_request to write a row (at most p_per_day run requests a UTC day, so
-- a held-down button cannot queue without limit) and analysis_requests_list to read the latest rows without their cards.
-- The worker and the Roundup use the service role, which bypasses row level security.
--
-- Idempotent: the table is created if absent, the functions are replaced.

create table if not exists public.analysis_requests (
  id            text primary key,
  kind          text not null check (kind in ('run', 'roundup')),
  finding       text not null,
  params        jsonb not null default '{}'::jsonb,
  status        text not null default 'queued' check (status in ('queued', 'running', 'done', 'failed')),
  note          text not null default '',          -- a failed run's plain reason; never a stack trace
  asked_at      timestamptz not null default now(),
  started_at    timestamptz,
  done_at       timestamptz,
  machine       text not null default '',
  card_id       text,
  card          jsonb                               -- the card as /analysis draws it, written by the worker
);
alter table public.analysis_requests enable row level security;
revoke all on public.analysis_requests from public, anon, authenticated;
create index if not exists analysis_requests_asked on public.analysis_requests (asked_at desc);
create index if not exists analysis_requests_queue on public.analysis_requests (status, asked_at) where status = 'queued';

create or replace function public.analysis_request(p_token text, p_kind text, p_finding text, p_params text, p_per_day integer default 24)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare
  secret text;
  today date := (now() at time zone 'utc')::date;
  n     integer;
  id    text;
  prm   jsonb;
begin
  select value into secret from erw_private.settings where key = 'internal_costs_token';
  if secret is null or length(secret) < 24 or p_token is null or p_token <> secret then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  if p_kind not in ('run', 'roundup') or p_finding is null or length(p_finding) < 3 or length(p_finding) > 120 then
    return jsonb_build_object('ok', false, 'reason', 'input');
  end if;
  begin
    prm := coalesce(p_params, '{}')::jsonb;
  exception when others then
    return jsonb_build_object('ok', false, 'reason', 'input');
  end;
  if length(prm::text) > 2000 then
    return jsonb_build_object('ok', false, 'reason', 'input');
  end if;
  if p_kind = 'run' then
    select count(*) into n from public.analysis_requests where kind = 'run' and (asked_at at time zone 'utc')::date = today;
    if n >= greatest(1, least(coalesce(p_per_day, 24), 200)) then
      return jsonb_build_object('ok', false, 'reason', 'day', 'requests_today', n);
    end if;
  end if;
  id := to_char(now() at time zone 'utc', 'YYYYMMDD"T"HH24MISS"Z"') || '-' || substr(md5(random()::text || clock_timestamp()::text), 1, 6);
  insert into public.analysis_requests (id, kind, finding, params, status, done_at)
    values (id, p_kind, p_finding, prm, case when p_kind = 'roundup' then 'done' else 'queued' end, case when p_kind = 'roundup' then now() else null end);
  return jsonb_build_object('ok', true, 'id', id);
end;
$$;
revoke all on function public.analysis_request(text, text, text, text, integer) from public;
grant execute on function public.analysis_request(text, text, text, text, integer) to anon, authenticated;

create or replace function public.analysis_requests_list(p_token text)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare
  secret text;
begin
  select value into secret from erw_private.settings where key = 'internal_costs_token';
  if secret is null or length(secret) < 24 or p_token is null or p_token <> secret then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  return coalesce((
    select jsonb_agg(r order by r.asked_at desc)
    from (
      select id, kind, finding, params, status, note, asked_at, started_at, done_at, machine, card_id
      from public.analysis_requests where kind = 'run' order by asked_at desc limit 50
    ) r), '[]'::jsonb);
end;
$$;
revoke all on function public.analysis_requests_list(text) from public;
grant execute on function public.analysis_requests_list(text) to anon, authenticated;
