-- Energy Research Warehouse (ERW): Supabase, migration 006 (session 21, ruling 7).
--
-- Separate opt-ins per subscriber: the daily Energy Digest and Energy Week, either or both
-- (the site's /subscribe has two checkboxes). warehouse/news/email_digest.py sends each kind only to
-- the addresses that chose it. At least one must be chosen. The anon key may still only insert.

alter table public.subscribers add column if not exists daily boolean not null default false;
alter table public.subscribers add column if not exists weekly boolean not null default false;

alter table public.subscribers drop constraint if exists subscribers_optin_check;
alter table public.subscribers add constraint subscribers_optin_check check (daily or weekly) not valid;

grant insert (email, source, daily, weekly) on public.subscribers to anon;
revoke select, update, delete, truncate on public.subscribers from anon, authenticated;
