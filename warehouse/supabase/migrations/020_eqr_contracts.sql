-- Energy Research Warehouse (ERW): Supabase, migration 020 (session 83).
--
-- FERC Electric Quarterly Report contracts, internal (never public):
--
--  - ferc_eqr_contracts (warehouse/connectors/ferc_eqr_contracts.py) reaches Supabase through load.py as an events table
--    with license internal, so row-level security hides it from the anon key, as it hides api_cost_ledger.
--  - internal_eqr_contracts(p_token, p_from, p_to, p_limit): the contract rows executed in [p_from, p_to), newest first,
--    for the review page /contracts. security definer, and only when p_token equals the secret the costs page uses
--    (erw_private.settings 'internal_costs_token', written by apply.py's full run; this migration does not touch it).
--  - internal_eqr_summary(p_token): the counts the page states (rows, rows with a numeric rate, by year of execution,
--    by product, by delivery balancing authority), over the rows the live set holds.
--
-- Apply this one alone: python warehouse/supabase/apply.py --only 020

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
             e.extra->>'x_quarter' as quarter
      from public.events e
      where e.table_name = 'ferc_eqr_contracts' and e.event_date >= p_from and e.event_date < p_to
      order by e.event_date desc, e.event_id
      limit least(greatest(coalesce(p_limit, 3000), 1), 5000)
    ) c), '[]'::jsonb);
end $$;
revoke all on function public.internal_eqr_contracts(text, date, date, integer) from public;
grant execute on function public.internal_eqr_contracts(text, date, date, integer) to anon;

create or replace function public.internal_eqr_summary(p_token text)
returns jsonb language plpgsql stable security definer set search_path = '' as $$
declare
  secret text;
begin
  select value into secret from erw_private.settings where key = 'internal_costs_token';
  if secret is null or length(secret) < 24 or p_token is null or p_token <> secret then
    raise exception 'not authorized' using errcode = '42501';
  end if;
  return (
    with r as (
      select e.event_date, e.extra, upper(coalesce(e.extra->>'x_product_name', '')) as product,
             coalesce(nullif(e.extra->>'x_point_of_delivery_balancing_authority', ''), 'not stated') as ba,
             (coalesce(e.extra->>'x_rate', '') <> '') as priced
      from public.events e where e.table_name = 'ferc_eqr_contracts'
    )
    select jsonb_build_object(
      'rows', (select count(*) from r),
      'priced', (select count(*) from r where priced),
      'first', (select to_char(min(event_date) at time zone 'UTC', 'YYYY-MM-DD') from r),
      'last', (select to_char(max(event_date) at time zone 'UTC', 'YYYY-MM-DD') from r),
      'quarters', (select coalesce(jsonb_agg(distinct extra->>'x_quarter'), '[]'::jsonb) from r),
      'by_month', (select coalesce(jsonb_agg(jsonb_build_object('month', m, 'rows', n, 'priced', p) order by m), '[]'::jsonb)
                   from (select to_char(event_date at time zone 'UTC', 'YYYY-MM') as m, count(*) as n, count(*) filter (where priced) as p
                         from r group by 1) t),
      'by_product', (select coalesce(jsonb_agg(jsonb_build_object('product', product, 'rows', n, 'priced', p) order by n desc, product), '[]'::jsonb)
                     from (select product, count(*) as n, count(*) filter (where priced) as p from r group by 1) t),
      'by_ba', (select coalesce(jsonb_agg(jsonb_build_object('ba', ba, 'rows', n) order by n desc, ba), '[]'::jsonb)
                from (select ba, count(*) as n from r group by 1) t)
    ));
end $$;
revoke all on function public.internal_eqr_summary(text) from public;
grant execute on function public.internal_eqr_summary(text) to anon;
