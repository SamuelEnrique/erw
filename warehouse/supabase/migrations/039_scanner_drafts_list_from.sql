-- Energy Research Warehouse (ERW), chain 507 (session 8900): the review list read page by page.
--
-- scanner_drafts_list (migration 029) returns at most 500 drafts, newest and strongest first. On 19 November 2026 the
-- table held 616 drafts, 549 of them the findings hunt's drafts that chain 506 audited, so /internal/findings never
-- showed the oldest 116: 50 audited drafts, 5 of them on the sheet of forty, could be neither seen nor approved there
-- (the state route found no such draft). This adds a function beside it, with the same token check, the same order and
-- the same columns, and an offset, so the site reads every page. Nothing of migration 029 changes; the site falls back to
-- the old function while this one is not applied.
create or replace function public.scanner_drafts_list_from(p_token text, p_offset integer default 0, p_limit integer default 500, p_state text default null)
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
      offset greatest(coalesce(p_offset, 0), 0)
      limit least(greatest(coalesce(p_limit, 500), 1), 500)
    ) r), '[]'::jsonb);
end;
$$;
revoke all on function public.scanner_drafts_list_from(text, integer, integer, text) from public;
grant execute on function public.scanner_drafts_list_from(text, integer, integer, text) to anon, authenticated;
