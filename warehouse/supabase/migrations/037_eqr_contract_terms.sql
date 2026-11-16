-- Energy Research Warehouse (ERW): Supabase, migration 037 (session 7019, chain 301; done-line request 19).
--
-- FERC Electric Quarterly Report contracts, internal (never public), for the review page /contracts:
-- internal_eqr_contracts(p_token, p_from, p_to, p_limit) answers six more fields of each row: x_begin_date, x_end_date,
-- x_increment_name, x_increment_peaking_name, x_rate_minimum, x_rate_maximum (of the 3,785 listed rows of energy,
-- capacity and tolling, 564 are drawn the same as another row of their agreement but for the price, and these fields
-- tell 326 of them apart). Same signature, same gate; the earlier keys are unchanged.
--
-- Request 22 (one party's line outside the 25 stored) is not here: serving it from the live set would load
-- ferc_eqr_party_totals, and session 102's rule keeps the internal EQR tables out of the live set
-- (tests/test_session102.py). It waits for the owner.
--
-- Not applied by a session: a migration beyond the live set's own is applied by a person
-- (warehouse/supabase/README.md, "A record of the migrations applied by hand"):
--
--     python warehouse/supabase/apply.py --only 037

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
             e.extra->>'x_rate_minimum' as rate_minimum, e.extra->>'x_rate_maximum' as rate_maximum
      from public.events e
      where e.table_name = 'ferc_eqr_contracts' and e.event_date >= p_from and e.event_date < p_to
      order by e.event_date desc, e.event_id
      limit least(greatest(coalesce(p_limit, 3000), 1), 5000)
    ) c), '[]'::jsonb);
end $$;
revoke all on function public.internal_eqr_contracts(text, date, date, integer) from public;
grant execute on function public.internal_eqr_contracts(text, date, date, integer) to anon;
