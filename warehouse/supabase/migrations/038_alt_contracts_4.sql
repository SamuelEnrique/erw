-- Energy Research Warehouse (ERW): Supabase, migration 038 (session 7701, 17 November 2026). Ruling alternative 4 of
-- /contracts, branch wip/alt-contracts-4: not a default on main, not for landing, never applied by a session.
--
-- internal_eqr_contracts(p_token, p_from, p_to, p_limit) answers three more fields of each row: filer (FERC's company
-- identifier of the filer, x_company_id), contract_id (x_contract_unique_id) and buyer_merged (x_buyer_counted_as: the
-- name the buyer is counted under by the rules of warehouse/derived/eqr_buyers.py, put on each contract row by the
-- branch's loader from ferc_eqr_buyer_names; no table of names enters the live set). With them the first view counts
-- contracts by filer and contract identifier, sellers by filer and buyers by merged name, as the other three views do.
-- Same signature, same gate; every earlier key is unchanged (migration 037's body, three keys added).
--
--     python warehouse/supabase/apply.py --only 038

create or replace function public.internal_eqr_contracts(p_token text, p_from date, p_to date, p_limit integer default 3000)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare
  secret text;
begin
  select value into secret from erw_private.settings where key = 'internal_costs_token';
  if secret is null or length(secret) < 24 or p_token is null or p_token <> secret then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  return coalesce((
    select jsonb_agg(c order by c.event_date desc, c.seller, c.event_id)
    from (
      select e.event_id, to_char(e.event_date at time zone 'UTC', 'YYYY-MM-DD') as event_date, e.status, e.mw, e.price,
             e.extra->>'x_seller_company_name' as seller, e.extra->>'x_customer_company_name' as buyer,
             e.extra->>'x_contract_affiliate' as affiliate, e.extra->>'x_contract_service_agreement_id' as agreement,
             e.extra->>'x_product_type_name' as product_type, e.extra->>'x_product_name' as product,
             e.extra->>'x_class_name' as class, e.extra->>'x_term_name' as term,
             e.extra->>'x_commencement_date_of_contract_term' as commencement,
             e.extra->>'x_contract_termination_date' as termination,
             e.extra->>'x_quantity' as quantity, e.extra->>'x_units' as units, e.extra->>'x_rate' as rate,
             e.extra->>'x_rate_units' as rate_units, e.extra->>'x_rate_description' as rate_description,
             e.extra->>'x_point_of_delivery_balancing_authority' as pod_ba,
             e.extra->>'x_point_of_delivery_specific_location' as pod_location,
             e.extra->>'x_quarter' as quarter,
             -- session 7019 (request 19): the row's own period, increment and rate bounds
             e.extra->>'x_begin_date' as begin_date, e.extra->>'x_end_date' as end_date,
             e.extra->>'x_increment_name' as increment, e.extra->>'x_increment_peaking_name' as increment_peaking,
             e.extra->>'x_rate_minimum' as rate_minimum, e.extra->>'x_rate_maximum' as rate_maximum,
             -- ruling alternative 4 of /contracts (wip/alt-contracts-4): the filer, the contract's identifier and the buyer's merged name
             e.extra->>'x_company_id' as filer, e.extra->>'x_contract_unique_id' as contract_id,
             e.extra->>'x_buyer_counted_as' as buyer_merged
      from public.events e
      where e.table_name = 'ferc_eqr_contracts' and e.event_date >= p_from and e.event_date < p_to
      order by e.event_date desc, e.event_id
      limit least(greatest(coalesce(p_limit, 3000), 1), 5000)
    ) c), '[]'::jsonb);
end $$;
revoke all on function public.internal_eqr_contracts(text, date, date, integer) from public;
grant execute on function public.internal_eqr_contracts(text, date, date, integer) to anon;
