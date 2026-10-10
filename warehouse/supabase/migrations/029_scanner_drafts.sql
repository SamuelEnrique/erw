-- Energy Research Warehouse (ERW): Supabase, migration 029 (session 181): the scanner's review list.
-- docs/methods/automated_analysis_scanner.md.
--
-- One internal table, public.scanner_drafts: a row per draft finding card the scanner raised
-- (warehouse/analysis/findings/findings_scanner.py). A draft is a flag and the card computed for it by code (chart,
-- callouts, footnote; no paragraph). It waits in state 'draft' until a person rules on it at /internal/findings:
--
--   approved          the card appears on /analysis, in the scanner's group, marked "Found by the scanner"
--   dismissed         it never appears anywhere but the review list's own history
--   full_card_asked   a full analysis was asked for it; request_id names the row of public.analysis_requests when the
--                     flag's series is one the impact study knows, else the row waits for a session to write the card
--
-- Each change of state is kept with its time: state_at holds the last one, state_history every one in order
-- ({state, from, at}). The flag (jsonb) is what makes a draft reproducible: the table, the series key, the dates, the
-- values, the threshold crossed and the scanner's version.
--
-- Internal means: row-level security is on, no policy exists, and every privilege of public, anon and authenticated
-- is revoked, so the site's public key reads and writes nothing in it. The table is in no live set and no Redivis
-- dataset. The site reaches it through two functions that check the internal token as migration 028's do
-- (erw_private.site_token_ok): scanner_drafts_list and scanner_draft_set_state. The anon key alone can execute them
-- and gets "not authorized". The data machine's worker adds drafts with the service role, which bypasses row-level
-- security.
--
-- One more function, for the request flow of /analysis (migration 027's table, unchanged): analysis_request_card
-- returns one run request with the card the worker wrote into its row. Until now the site could list the requests
-- (analysis_requests_list, without the cards) and a done card could be read only after its file was committed and
-- deployed; a card asked for on the site, the impact study's among them, is now read from the row where it was asked.
-- Behind the same token; it reads and never writes.
--
-- Safe to run again: the table is created if absent, the functions are replaced. Nothing existing is changed.
-- Rollback: ../rollbacks/029_scanner_drafts.sql, applied with apply.py --rollback 029 (it drops the table with its
-- drafts and the three functions).

create table if not exists public.scanner_drafts (
  id              text primary key check (id ~ '^scan-[a-z]+-[0-9a-f]{12}$'),
  flag_key        text not null,                      -- rule|table|series: one open draft per key
  rule            text not null check (rule in ('record', 'negative', 'spike', 'weekly', 'pair')),
  table_name      text not null,
  series_key      text not null,
  flag_date       date not null,
  value           double precision,
  strength        double precision not null default 0,
  scanner_version text not null,
  flag            jsonb not null,
  card            jsonb not null,
  state           text not null default 'draft' check (state in ('draft', 'approved', 'dismissed', 'full_card_asked')),
  raised_at       timestamptz not null default now(),
  state_at        timestamptz,
  state_history   jsonb not null default '[]'::jsonb,
  request_id      text
);
alter table public.scanner_drafts enable row level security;
revoke all on public.scanner_drafts from public, anon, authenticated;
create index if not exists scanner_drafts_state on public.scanner_drafts (state, raised_at desc);
create index if not exists scanner_drafts_key on public.scanner_drafts (flag_key);

-- The drafts, newest and strongest first: by the UTC day they were raised, then by strength. p_state null: every state.
create or replace function public.scanner_drafts_list(p_token text, p_state text default null, p_limit integer default 100)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
begin
  if not erw_private.site_token_ok(p_token) then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  if p_state is not null and p_state not in ('draft', 'approved', 'dismissed', 'full_card_asked') then
    return '[]'::jsonb;
  end if;
  return coalesce((
    select jsonb_agg(to_jsonb(r) - 'raised_day' order by r.raised_day desc, r.strength desc, r.id)
    from (
      select id, rule, table_name, series_key, flag_date, value, strength, scanner_version, state, raised_at, state_at,
             state_history, request_id, card, (raised_at at time zone 'utc')::date as raised_day
      from public.scanner_drafts
      where p_state is null or state = p_state
      order by (raised_at at time zone 'utc')::date desc, strength desc, id
      limit least(greatest(coalesce(p_limit, 100), 1), 500)
    ) r), '[]'::jsonb);
end;
$$;
revoke all on function public.scanner_drafts_list(text, text, integer) from public;
grant execute on function public.scanner_drafts_list(text, text, integer) to anon, authenticated;

-- One draft's state, changed, with the time of the change kept. p_request_id: the analysis request queued for a full card.
create or replace function public.scanner_draft_set_state(p_token text, p_id text, p_state text, p_request_id text default null)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare
  was  text;
  at_  timestamptz := now();
begin
  if not erw_private.site_token_ok(p_token) then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  if p_id is null or p_id !~ '^scan-[a-z]+-[0-9a-f]{12}$' or p_state is null
     or p_state not in ('draft', 'approved', 'dismissed', 'full_card_asked')
     or (p_request_id is not null and length(p_request_id) > 60) then
    return jsonb_build_object('ok', false, 'reason', 'input');
  end if;
  select state into was from public.scanner_drafts where id = p_id for update;
  if not found then
    return jsonb_build_object('ok', false, 'reason', 'no such draft');
  end if;
  update public.scanner_drafts
     set state = p_state,
         state_at = at_,
         state_history = state_history || jsonb_build_array(jsonb_build_object(
           'state', p_state, 'from', was, 'at', to_char(at_ at time zone 'utc', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'))),
         request_id = coalesce(p_request_id, request_id)
   where id = p_id;
  return jsonb_build_object('ok', true, 'id', p_id, 'state', p_state, 'from', was,
                            'at', to_char(at_ at time zone 'utc', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'));
end;
$$;
revoke all on function public.scanner_draft_set_state(text, text, text, text) from public;
grant execute on function public.scanner_draft_set_state(text, text, text, text) to anon, authenticated;

-- One run request with its card (null until the worker has written it). A request that is not there answers null.
create or replace function public.analysis_request_card(p_token text, p_id text)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
begin
  if not erw_private.site_token_ok(p_token) then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  if p_id is null or p_id !~ '^[A-Za-z0-9-]{6,60}$' then
    return null;
  end if;
  return (
    select jsonb_build_object('id', r.id, 'finding', r.finding, 'params', r.params, 'status', r.status, 'note', r.note,
                              'asked_at', r.asked_at, 'done_at', r.done_at, 'card_id', r.card_id, 'card', r.card)
    from public.analysis_requests r where r.id = p_id and r.kind = 'run');
end;
$$;
revoke all on function public.analysis_request_card(text, text) from public;
grant execute on function public.analysis_request_card(text, text) to anon, authenticated;
