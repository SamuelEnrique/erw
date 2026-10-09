-- Energy Research Warehouse (ERW), session 169: Thesis Builder (/thesis, in review), the gate on the niche.
--
-- The owner's ruling of 8 October 2026: a sector or a market topic is refused on /thesis before a run is queued, and
-- "a Run anyway box, stored with the run and flagged on its report". This migration gives the run a place for that:
--
--   1. public.thesis_runs.gate (jsonb, null on every run that was not forced): what the gate read of the niche when
--      the run was started with the box ticked, {"forced": true, "why": ..., "topic": ..., "at": ...}
--      (site/lib/thesis/niche.ts, forcedOf). The runner copies it onto the run's report (warehouse/thesis/run.py), and
--      the page flags the report. A run that passed the gate holds null here, as every run before this migration does.
--   2. public.thesis_submit_forced(p_token, p_niche, p_stage, p_geography, p_gate): queues a forced run. It calls
--      public.thesis_submit (migration 024), so the internal token, the limits on the fields, the count of the day's
--      runs and the dispatch of thesis.yml are that function's, unchanged; then it writes the gate on the new row, in
--      the same transaction (the dispatch leaves through pg_net only when the transaction commits, so the runner
--      never reads the row without its gate).
--   3. the site's cost ledger (public.site_api_calls, migration 010 and 023) admits the step 'site_thesis_gate': the
--      gate's one small model call for an input its curated table does not hold. Until this is applied that row is
--      refused by the check and the refusal is swallowed (the call itself is not affected).
--
-- Nothing of migration 024 or 025 is replaced: no function, no policy, no grant. One nullable column is added to
-- thesis_runs; row level security stays on with no policy, and the public key still reads and writes nothing in it.
--
-- Idempotent: the column is added if absent, the function is replaced, the check is dropped and added again.

alter table public.thesis_runs add column if not exists gate jsonb;      -- null: the run passed the gate

create or replace function public.thesis_submit_forced(p_token text, p_niche text, p_stage text, p_geography text, p_gate jsonb)
returns jsonb language plpgsql volatile security definer set search_path = '' as $$
declare
  r jsonb;
begin
  -- thesis_submit checks the token first and raises when it is wrong; nothing is said before that
  if not public.thesis_token_ok(p_token) then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  if p_gate is null or jsonb_typeof(p_gate) is distinct from 'object' or (p_gate ->> 'forced') is distinct from 'true' or length(p_gate::text) > 2000 then
    return jsonb_build_object('ok', false, 'reason', 'input');
  end if;
  r := public.thesis_submit(p_token, p_niche, p_stage, p_geography);
  if (r ->> 'ok') = 'true' then
    update public.thesis_runs set gate = p_gate where run_id = r ->> 'run_id';
  end if;
  return r;
end;
$$;
revoke all on function public.thesis_submit_forced(text, text, text, text, jsonb) from public;
grant execute on function public.thesis_submit_forced(text, text, text, text, jsonb) to anon, authenticated;

alter table public.site_api_calls drop constraint if exists site_api_calls_step_check;
alter table public.site_api_calls add constraint site_api_calls_step_check check (step in ('site_ask', 'site_ask_ercot', 'site_thesis_gate'));
