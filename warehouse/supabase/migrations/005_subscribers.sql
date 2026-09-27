-- Energy Research Warehouse (ERW): Supabase, migration 005 (session 19).
--
-- Email subscribers for the Energy Digest (the site's /subscribe; warehouse/news/email.py).
-- Insert-only for the anon key: the public site can add an address and nothing else. No
-- select, update or delete policy exists for anon, and the select privilege is revoked, so
-- an address can never be read back through the anon key (not even to say "already
-- subscribed": there is no unique constraint, and duplicates are removed when sending).
-- Only the service role reads the table. It is not an ERW table: it holds no source data,
-- is not in coverage, and is never uploaded to Redivis.

create table if not exists public.subscribers (
  id          bigint generated always as identity primary key,
  email       text not null
              check (length(email) between 3 and 254 and email ~ '^[^@[:space:]]+@[^@[:space:]]+\.[^@[:space:]]+$'),
  created_at  timestamptz not null default now(),
  source      text not null default 'site' check (source in ('site'))
);

alter table public.subscribers enable row level security;

drop policy if exists anon_insert on public.subscribers;
create policy anon_insert on public.subscribers for insert to anon with check (source = 'site');

grant insert (email, source) on public.subscribers to anon;
revoke select, update, delete, truncate on public.subscribers from anon, authenticated;
