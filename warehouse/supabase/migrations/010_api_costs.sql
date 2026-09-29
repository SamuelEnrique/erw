-- Energy Research Warehouse (ERW): Supabase, migration 010 (session 30, Part B1).
--
-- The Anthropic API cost ledger, internal (never public):
--
--  - The warehouse's ledger (api_cost_ledger, written by warehouse/llm.py on every model call of the daily run and
--    of sessions) reaches Supabase through load.py as an events table with license internal, so row-level security
--    already hides it from the anon key.
--  - site_api_calls: the site's own calls (the /ask question answering, site/lib/chat/ledger.ts). The site holds only
--    the anon key, so the anon key may insert a row here, as it may into subscribers, and may not read, update or
--    delete one.
--  - internal_costs(p_token): the rows of both, last 35 days, for the site's /internal/costs page. security definer, so
--    it reads what the anon key cannot, and only when p_token equals the secret in erw_private.settings
--    ('internal_costs_token'). warehouse/supabase/apply.py writes that secret from INTERNAL_COSTS_TOKEN in the
--    environment; no migration holds it. Without the secret set, the function answers nothing to anyone.

create table if not exists public.site_api_calls (
  id                  bigint generated always as identity primary key,
  ts_utc              timestamptz not null default now(),
  step                text        not null check (step in ('site_ask')),
  model               text        not null check (length(model) between 1 and 64),
  input_tokens        integer     not null check (input_tokens between 0 and 2000000),
  cached_input_tokens integer     not null default 0 check (cached_input_tokens between 0 and 2000000),
  cache_write_tokens  integer     not null default 0 check (cache_write_tokens between 0 and 2000000),
  output_tokens       integer     not null check (output_tokens between 0 and 200000),
  usd                 numeric     check (usd is null or (usd >= 0 and usd < 100)),
  request_id          text        check (request_id is null or length(request_id) < 128)
);
alter table public.site_api_calls enable row level security;
revoke all on public.site_api_calls from public, anon, authenticated;
grant insert (step, model, input_tokens, cached_input_tokens, cache_write_tokens, output_tokens, usd, request_id)
  on public.site_api_calls to anon;
drop policy if exists anon_insert on public.site_api_calls;
create policy anon_insert on public.site_api_calls for insert to anon with check (true);

create or replace function public.internal_costs(p_token text)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare
  secret text;
begin
  select value into secret from erw_private.settings where key = 'internal_costs_token';
  if secret is null or length(secret) < 24 or p_token is null or p_token <> secret then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  return coalesce((
    select jsonb_agg(c order by c.ts_utc)
    from (
      select e.event_date as ts_utc, e.extra->>'session' as session, e.extra->>'step' as step,
             e.extra->>'model' as model, nullif(e.extra->>'input_tokens', '')::bigint as input_tokens,
             nullif(e.extra->>'cached_input_tokens', '')::bigint as cached_input_tokens,
             nullif(e.extra->>'cache_write_tokens', '')::bigint as cache_write_tokens,
             nullif(e.extra->>'output_tokens', '')::bigint as output_tokens,
             nullif(e.extra->>'usd', '')::numeric as usd
      from public.events e
      where e.table_name = 'api_cost_ledger' and e.event_date >= now() - interval '35 days'
      union all
      select s.ts_utc, 'site', s.step, s.model, s.input_tokens, s.cached_input_tokens, s.cache_write_tokens,
             s.output_tokens, s.usd
      from public.site_api_calls s
      where s.ts_utc >= now() - interval '35 days'
    ) c), '[]'::jsonb);
end $$;
revoke all on function public.internal_costs(text) from public;
grant execute on function public.internal_costs(text) to anon;
