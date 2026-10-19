-- Energy Research Warehouse (ERW): Supabase, migration 035 (session 314): an evaluation's own ledger step.
-- The owner's ruling of 19 October 2026 on session 302's open item: an evaluation of the question-answering tools
-- (thirty questions through /api/ask as the pages ask, sessions 302 and 320) spends through a ledger step of its own,
-- site_ask_eval, never the public day ceiling. Two changes, nothing a page reads:
--   1. site_api_calls accepts the step (migration 023's check allowed site_ask and site_ask_ercot alone);
--   2. site_ask_admit, the public ceilings (session 128), sums the public steps alone: the evaluation's rows are left out
--      of the day's and the month's spend and of the unpriced count. internal_ask_spend (migration 023) groups by day
--      and step already, so /internal/ask shows the evaluation's line of its own, and the site reads the evaluation's
--      day spend from it (site/lib/chat/limits.ts, admitEvaluation, against ASK_EVAL_DAILY_USD).
-- The site of session 314 writes the step only for a request that carries ASK_EVAL_TOKEN (a secret set on the server
-- that runs the evaluation, a local site; never on Vercel). Until this migration is applied such a write is refused by
-- the check and the evaluation's question fails (the site writes the step strictly, lib/chat/ledger.ts), so an
-- evaluation never spends unrecorded. The function's grants (migration 034: service_role alone) are kept by create or
-- replace. Rollback: rollbacks/035_ask_eval_step.sql.

alter table public.site_api_calls drop constraint if exists site_api_calls_step_check;
alter table public.site_api_calls add constraint site_api_calls_step_check check (step in ('site_ask', 'site_ask_ercot', 'site_ask_eval'));

create or replace function public.site_ask_admit(p_visitor text, p_per_visitor integer, p_day_usd numeric, p_month_usd numeric)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare
  today      date := (now() at time zone 'utc')::date;
  day_start  timestamptz := (today::timestamp) at time zone 'utc';
  mon_start  timestamptz := (date_trunc('month', today::timestamp)) at time zone 'utc';
  month_usd  numeric;
  day_usd    numeric;
  unpriced   integer;
  seen       integer;
  visitors   integer;
begin
  if p_visitor is null or p_visitor !~ '^[0-9a-f]{32}$' or p_per_visitor is null or p_per_visitor < 0
     or p_day_usd is null or p_day_usd < 0 or p_month_usd is null or p_month_usd < 0 then
    return jsonb_build_object('ok', false, 'reason', 'config');
  end if;
  delete from public.site_ask_counts where day < today;   -- only today's counts are kept
  -- session 314: the public steps alone; an evaluation's rows (site_ask_eval) have a ceiling of their own
  select coalesce(sum(usd), 0), count(*) filter (where usd is null) into month_usd, unpriced
    from public.site_api_calls where ts_utc >= mon_start and step <> 'site_ask_eval';
  if unpriced > 0 then
    return jsonb_build_object('ok', false, 'reason', 'unpriced');   -- a call with no price: the spend cannot be counted
  end if;
  if month_usd >= p_month_usd then
    return jsonb_build_object('ok', false, 'reason', 'month');
  end if;
  select coalesce(sum(usd), 0) into day_usd from public.site_api_calls where ts_utc >= day_start and step <> 'site_ask_eval';
  if day_usd >= p_day_usd then
    return jsonb_build_object('ok', false, 'reason', 'day');
  end if;
  select n into seen from public.site_ask_counts where day = today and visitor = p_visitor;
  if coalesce(seen, 0) >= p_per_visitor then
    return jsonb_build_object('ok', false, 'reason', 'visitor');
  end if;
  if seen is null then
    select count(*) into visitors from public.site_ask_counts where day = today;
    if visitors >= 20000 then
      return jsonb_build_object('ok', false, 'reason', 'busy');   -- the count is never allowed to grow without end
    end if;
  end if;
  insert into public.site_ask_counts (day, visitor, n) values (today, p_visitor, 1)
    on conflict (day, visitor) do update set n = public.site_ask_counts.n + 1;
  return jsonb_build_object('ok', true, 'reason', null);
end;
$$;
