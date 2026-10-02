-- Energy Research Warehouse (ERW), session 59: the scheduled jobs, triggered from the database on time.
--
-- GitHub runs this repository's scheduled workflows late or not at all (session 54: a 15-minute cron ran five times a
-- day; session 58: the daily job came hours late). pg_cron fires on time and pg_net calls GitHub's workflow_dispatch;
-- GitHub runs the workflow at once. The token (a fine-grained GitHub token, Actions read and write on SamuelEnrique/erw
-- only) is in Supabase Vault under the name github_dispatch, written by warehouse/supabase/scheduler.py from the
-- environment: it is never in this repository. The daily job and the Roundup are dispatched with once=1, so their gate
-- job (session 58) skips a second run on a day one already succeeded, whichever trigger came first.
--
-- Idempotent: the extensions and the function are created if absent or replaced; each job is unscheduled and scheduled
-- again by name.

create extension if not exists pg_cron;
create extension if not exists pg_net;

create or replace function public.erw_dispatch(workflow text, body jsonb default '{"ref":"main"}'::jsonb)
returns bigint
language plpgsql
security definer
set search_path = public, extensions
as $$
declare
  tok text;
  id bigint;
begin
  select decrypted_secret into tok from vault.decrypted_secrets where name = 'github_dispatch';
  if tok is null then
    raise exception 'erw_dispatch: no github_dispatch secret in Vault (warehouse/supabase/scheduler.py --set-token)';
  end if;
  select net.http_post(
    url := 'https://api.github.com/repos/SamuelEnrique/erw/actions/workflows/' || workflow || '/dispatches',
    body := body,
    headers := jsonb_build_object('Accept', 'application/vnd.github+json', 'X-GitHub-Api-Version', '2022-11-28',
                                  'Authorization', 'Bearer ' || tok, 'User-Agent', 'erw-scheduler', 'Content-Type', 'application/json'),
    timeout_milliseconds := 20000
  ) into id;
  return id;
end;
$$;
-- only the database's own roles (pg_cron runs as postgres) may call it: never the site's anon key
revoke all on function public.erw_dispatch(text, jsonb) from public, anon, authenticated;

do $$
declare j text;
begin
  foreach j in array array['erw-daily', 'erw-latest-prices', 'erw-hourly-network', 'erw-roundup', 'erw-weekly-vacuum'] loop
    if exists (select 1 from cron.job where jobname = j) then
      perform cron.unschedule(j);
    end if;
  end loop;
end $$;

-- UTC, as pg_cron runs in the database's time zone (UTC on Supabase)
select cron.schedule('erw-daily', '0 14 * * *',
  $$select public.erw_dispatch('daily-prices.yml', '{"ref":"main","inputs":{"queues":"0","once":"1"}}'::jsonb)$$);
select cron.schedule('erw-latest-prices', '*/15 * * * *',
  $$select public.erw_dispatch('latest-prices.yml')$$);
select cron.schedule('erw-hourly-network', '5 0-13,15-23 * * *',
  $$select public.erw_dispatch('hourly-network.yml')$$);
select cron.schedule('erw-roundup', '0 23 * * 0',
  $$select public.erw_dispatch('roundup.yml', '{"ref":"main","inputs":{"once":"1"}}'::jsonb)$$);
select cron.schedule('erw-weekly-vacuum', '0 10 * * 0',
  $$select public.erw_dispatch('weekly-vacuum.yml')$$);
