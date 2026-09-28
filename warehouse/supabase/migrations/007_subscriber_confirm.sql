-- Energy Research Warehouse (ERW): Supabase, migration 007 (session 23).
--
-- Topics, double opt-in and a tokened unsubscribe for the email list (the site's /subscribe;
-- warehouse/news/email_digest.py). Human ruling, session 21: nothing is sent to the list before an
-- address is confirmed, and every email carries an unsubscribe link.
--
--  - topics: the ten topics a subscriber chose (the email filters the top stories to them; the website
--    digest stays complete). The anon key may insert them with the address, and still may not read.
--  - confirmed_at: set when the address follows the signed link in its confirmation email.
--  - unsubscribed_at: set when the address follows the signed unsubscribe link in any email.
--  - email_suppressions: every address that unsubscribed, by address, so the sender also leaves out a
--    fixed recipient (DIGEST_RECIPIENTS) who unsubscribed. Readable by the service role only.
--  - The link's token is HMAC-SHA256(lower(email) || ':' || purpose, secret), in hex. The secret lives in
--    erw_private.settings (a schema the API does not expose; no grant to anon) and in the environment of
--    the site and the sender (EMAIL_TOKEN_SECRET); warehouse/supabase/apply.py writes it from the environment,
--    and no migration holds it.
--  - subscribe_confirm and subscribe_unsubscribe check the token in the database (security definer), so the
--    anon key can confirm or unsubscribe only an address whose token it was given, and still reads nothing.

create schema if not exists erw_private;
revoke all on schema erw_private from public, anon, authenticated;
create table if not exists erw_private.settings (key text primary key, value text not null);
revoke all on erw_private.settings from public, anon, authenticated;

alter table public.subscribers add column if not exists topics text[] not null default array[
  'power_prices', 'gas_lng', 'oil', 'nuclear', 'renewables_storage', 'transmission_grid', 'datacenters_ai',
  'deals_capital', 'policy', 'geopolitics'];
alter table public.subscribers add column if not exists confirmed_at timestamptz;
alter table public.subscribers add column if not exists unsubscribed_at timestamptz;

alter table public.subscribers drop constraint if exists subscribers_topics_check;
alter table public.subscribers add constraint subscribers_topics_check check (
  cardinality(topics) between 1 and 10 and topics <@ array[
    'power_prices', 'gas_lng', 'oil', 'nuclear', 'renewables_storage', 'transmission_grid', 'datacenters_ai',
    'deals_capital', 'policy', 'geopolitics']::text[]);

create table if not exists public.email_suppressions (
  email      text primary key,
  created_at timestamptz not null default now()
);
alter table public.email_suppressions enable row level security;
revoke all on public.email_suppressions from anon, authenticated;

grant insert (email, source, daily, weekly, topics) on public.subscribers to anon;
revoke select, update, delete, truncate on public.subscribers from anon, authenticated;

create or replace function erw_private.email_token(p_email text, p_purpose text)
returns text language sql stable security definer set search_path = '' as $$
  select encode(extensions.hmac(lower(trim(p_email)) || ':' || p_purpose,
                                (select value from erw_private.settings where key = 'email_token_secret'), 'sha256'), 'hex')
$$;
revoke all on function erw_private.email_token(text, text) from public, anon, authenticated;

create or replace function public.subscribe_confirm(p_email text, p_token text)
returns boolean language plpgsql security definer set search_path = '' as $$
begin
  if p_token is null or p_token <> erw_private.email_token(p_email, 'confirm') then
    return false;
  end if;
  update public.subscribers set confirmed_at = now()
   where lower(email) = lower(trim(p_email)) and confirmed_at is null and unsubscribed_at is null;
  delete from public.email_suppressions where email = lower(trim(p_email));
  return true;
end $$;

create or replace function public.subscribe_unsubscribe(p_email text, p_token text)
returns boolean language plpgsql security definer set search_path = '' as $$
begin
  if p_token is null or p_token <> erw_private.email_token(p_email, 'unsubscribe') then
    return false;
  end if;
  update public.subscribers set unsubscribed_at = now()
   where lower(email) = lower(trim(p_email)) and unsubscribed_at is null;
  insert into public.email_suppressions (email) values (lower(trim(p_email))) on conflict (email) do nothing;
  return true;
end $$;

revoke all on function public.subscribe_confirm(text, text) from public;
revoke all on function public.subscribe_unsubscribe(text, text) from public;
grant execute on function public.subscribe_confirm(text, text) to anon, authenticated;
grant execute on function public.subscribe_unsubscribe(text, text) to anon, authenticated;
