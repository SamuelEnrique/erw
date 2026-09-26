-- Energy Research Warehouse (ERW): Supabase live set, migration 002 (session 10).
--
-- Row-level security on every table. An anonymous reader (the anon key, used by
-- the public site) sees only rows whose license is 'public'. Nobody but the
-- service role writes: there are no insert, update or delete policies, and the
-- service role (warehouse/supabase/load.py, latest_prices.py) bypasses RLS.
-- Internal rows (PJM, CARB, RGGI, FRED IMF, PortWatch, news_stories) never reach
-- an anonymous reader.

alter table public.series        enable row level security;
alter table public.entities      enable row level security;
alter table public.events        enable row level security;
alter table public.latest_prices enable row level security;
alter table public.catalogue     enable row level security;
alter table public.sources       enable row level security;
alter table public.headers       enable row level security;

drop policy if exists public_rows on public.series;
create policy public_rows on public.series for select to anon, authenticated using (license = 'public');
drop policy if exists public_rows on public.entities;
create policy public_rows on public.entities for select to anon, authenticated using (license = 'public');
drop policy if exists public_rows on public.events;
create policy public_rows on public.events for select to anon, authenticated using (license = 'public');
drop policy if exists public_rows on public.latest_prices;
create policy public_rows on public.latest_prices for select to anon, authenticated using (license = 'public');
drop policy if exists public_rows on public.catalogue;
create policy public_rows on public.catalogue for select to anon, authenticated using (license = 'public');
drop policy if exists public_rows on public.sources;
create policy public_rows on public.sources for select to anon, authenticated using (license = 'public');
drop policy if exists public_rows on public.headers;
create policy public_rows on public.headers for select to anon, authenticated using (license = 'public');

-- Reading needs the table privilege as well as a policy.
grant select on public.series, public.entities, public.events, public.latest_prices,
                public.catalogue, public.sources, public.headers to anon, authenticated;
revoke insert, update, delete, truncate on public.series, public.entities, public.events,
                public.latest_prices, public.catalogue, public.sources, public.headers from anon, authenticated;
