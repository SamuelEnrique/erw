-- Energy Research Warehouse (ERW): Supabase, migration 021 (session 90).
--
-- The contracts page's summary, computed once when the table is loaded and not on every request.
--
-- Migration 020's internal_eqr_summary(p_token) counted the 19,009 live rows of ferc_eqr_contracts five ways on each
-- call. It is called with the public key, whose statements are cancelled after 3 seconds, and on production the count
-- took longer: /contracts answered "canceling statement due to statement timeout" where its panel should be.
--
--  - erw_private.eqr_summary: one row, the summary as the loader computed it from the rows it loaded
--    (warehouse/supabase/load.py, eqr_summary), with the number of rows it counted and when.
--  - eqr_summary_store(p_summary): writes that row. The service key only: the loader calls it after it loads the table.
--  - internal_eqr_summary(p_token): the same name, arguments and answer as before, now one row read. It still answers
--    only with the internal token. Before the first store it raises, and says what to run.
--
-- Apply this one alone: python warehouse/supabase/apply.py --only 021

create table if not exists erw_private.eqr_summary (
  id boolean primary key default true check (id),
  summary jsonb not null,
  n_rows bigint not null,
  computed_at timestamptz not null default now()
);
revoke all on erw_private.eqr_summary from public, anon, authenticated;

create or replace function public.eqr_summary_store(p_summary jsonb)
returns jsonb language plpgsql security definer set search_path = '' as $$
declare
  n bigint;
begin
  n := (p_summary->>'rows')::bigint;
  if n is null or n < 0 or jsonb_typeof(p_summary->'by_month') <> 'array' or jsonb_typeof(p_summary->'by_product') <> 'array'
     or jsonb_typeof(p_summary->'by_ba') <> 'array' or jsonb_typeof(p_summary->'quarters') <> 'array' then
    raise exception 'not a contracts summary' using errcode = '22023';
  end if;
  insert into erw_private.eqr_summary (id, summary, n_rows, computed_at) values (true, p_summary, n, now())
  on conflict (id) do update set summary = excluded.summary, n_rows = excluded.n_rows, computed_at = excluded.computed_at;
  return jsonb_build_object('rows', n, 'computed_at', to_char(now() at time zone 'UTC', 'YYYY-MM-DD"T"HH24:MI:SS"Z"'));
end $$;
revoke all on function public.eqr_summary_store(jsonb) from public;
revoke all on function public.eqr_summary_store(jsonb) from anon, authenticated;
grant execute on function public.eqr_summary_store(jsonb) to service_role;

create or replace function public.internal_eqr_summary(p_token text)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare
  secret text;
  s jsonb;
begin
  select value into secret from erw_private.settings where key = 'internal_costs_token';
  if secret is null or length(secret) < 24 or p_token is null or p_token <> secret then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  select summary into s from erw_private.eqr_summary where id;
  if s is null then
    raise exception 'the contracts summary is not computed yet: python warehouse/supabase/load.py --only ferc_eqr_contracts' using errcode = 'P0002';
  end if;
  return s;
end $$;
revoke all on function public.internal_eqr_summary(text) from public;
grant execute on function public.internal_eqr_summary(text) to anon;
