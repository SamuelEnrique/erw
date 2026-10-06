-- Energy Research Warehouse (ERW): Supabase, migration 023 (session 128): the question-answering tools made safe to open.
--
-- Four things, all for /api/ask (the general chat and Ask ERCOT). Nothing here is a table a page reads.
--
--  1. site_api_calls takes Ask ERCOT's rows. Its step check allowed only 'site_ask'; since session 121 the site has
--     recorded Ask ERCOT's calls as 'site_ask_ercot', the check refused every one, and the write's failure is swallowed
--     by design. So no Ask ERCOT call has ever reached the ledger. The check now allows both.
--  2. Each question's cost. question_id: 32 hexadecimal characters the server draws at random for a question (it is
--     not made from anything about the visitor); every model call of that question carries it, so a question's cost
--     is the sum of its rows.
--  3. The count of questions per visitor per day. site_ask_counts holds, for today only, a keyed hash and a count.
--     The hash is made by the server from the visitor's address, the day and a secret the database never sees
--     (site/lib/chat/limits.ts): it cannot be turned back into an address, and it is another value the next day, so a
--     visitor cannot be followed from one day to the next. No address, no question and no time is stored. Every call
--     of site_ask_admit deletes the rows of earlier days.
--  4. site_ask_admit: one call before a question is sent to a model. It answers ok, or the reason the question is
--     not admitted: the month's spend has reached its ceiling ('month'), the day's has ('day'), a call in the ledger
--     has no price so the spend cannot be counted ('unpriced'), the visitor has asked the day's number ('visitor'), or
--     the day holds too many visitors to count ('busy'). The ceilings and the number are the caller's (the site reads
--     them from its configuration); the function holds no number of its own. The anon key may execute it and may
--     read neither table. It returns no spend figure: a caller learns only yes or no.
--     A caller who passes its own high ceilings learns "ok" and nothing else: no model is called by this function.
--  5. internal_ask_spend(p_token): spend and questions by day and step, for the internal view (/internal/ask), behind
--     the same secret as internal_costs.
--
-- Days are UTC days. Safe to run again.

alter table public.site_api_calls drop constraint if exists site_api_calls_step_check;
alter table public.site_api_calls add constraint site_api_calls_step_check check (step in ('site_ask', 'site_ask_ercot'));
alter table public.site_api_calls add column if not exists question_id text;
alter table public.site_api_calls drop constraint if exists site_api_calls_question_id_check;
alter table public.site_api_calls add constraint site_api_calls_question_id_check check (question_id is null or question_id ~ '^[0-9a-f]{32}$');
grant insert (question_id) on public.site_api_calls to anon;

create table if not exists public.site_ask_counts (
  day     date    not null,
  visitor text    not null check (visitor ~ '^[0-9a-f]{32}$'),
  n       integer not null default 0 check (n >= 0),
  primary key (day, visitor)
);
alter table public.site_ask_counts enable row level security;
revoke all on public.site_ask_counts from public, anon, authenticated;

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
revoke all on function public.site_ask_admit(text, integer, numeric, numeric) from public;
grant execute on function public.site_ask_admit(text, integer, numeric, numeric) to anon, authenticated;

create or replace function public.internal_ask_spend(p_token text)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare
  secret text;
  today  date := (now() at time zone 'utc')::date;
begin
  select value into secret from erw_private.settings where key = 'internal_costs_token';
  if secret is null or length(secret) < 24 or p_token is null or p_token <> secret then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  return jsonb_build_object(
    'today', today,
    'days', coalesce((
      select jsonb_agg(d order by d.day, d.step)
      from (
        select (ts_utc at time zone 'utc')::date as day, step, count(*) as calls, count(distinct question_id) as questions,
               count(*) filter (where question_id is null) as calls_without_question, coalesce(sum(usd), 0) as usd,
               count(*) filter (where usd is null) as unpriced
        from public.site_api_calls
        where ts_utc >= ((today - 62)::timestamp) at time zone 'utc'
        group by 1, 2
      ) d), '[]'::jsonb),
    'costliest', coalesce((
      select jsonb_agg(q order by q.usd desc)
      from (
        select (min(ts_utc) at time zone 'utc')::date as day, step, count(*) as calls, sum(usd) as usd
        from public.site_api_calls
        where question_id is not null and ts_utc >= ((today - 62)::timestamp) at time zone 'utc'
        group by question_id, step order by sum(usd) desc nulls last limit 10
      ) q), '[]'::jsonb),
    'visitors_today', (select count(*) from public.site_ask_counts where day = today),
    'questions_today', (select coalesce(sum(n), 0) from public.site_ask_counts where day = today)
  );
end;
$$;
revoke all on function public.internal_ask_spend(text) from public;
grant execute on function public.internal_ask_spend(text) to anon, authenticated;
