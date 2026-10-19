-- Energy Research Warehouse (ERW): Supabase, the rollback of migration 035 (session 314): the step check and the
-- public ceilings' sums as migration 023 left them. A row already written under site_ask_eval would fail the restored
-- check, so those rows are moved to site_ask first (their question ids and costs stay; /internal/ask then counts them
-- with the public chat's). The function's grants (migration 034) are kept by create or replace.

update public.site_api_calls set step = 'site_ask' where step = 'site_ask_eval';
alter table public.site_api_calls drop constraint if exists site_api_calls_step_check;
alter table public.site_api_calls add constraint site_api_calls_step_check check (step in ('site_ask', 'site_ask_ercot'));

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
  select coalesce(sum(usd), 0), count(*) filter (where usd is null) into month_usd, unpriced
    from public.site_api_calls where ts_utc >= mon_start;
  if unpriced > 0 then
    return jsonb_build_object('ok', false, 'reason', 'unpriced');   -- a call with no price: the spend cannot be counted
  end if;
  if month_usd >= p_month_usd then
    return jsonb_build_object('ok', false, 'reason', 'month');
  end if;
  select coalesce(sum(usd), 0) into day_usd from public.site_api_calls where ts_utc >= day_start;
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
