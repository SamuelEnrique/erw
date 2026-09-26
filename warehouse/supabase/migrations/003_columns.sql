-- Energy Research Warehouse (ERW): Supabase live set, migration 003 (session 11).
--
-- The column list of each live-set table, in the order of its CSV header, as a
-- JSON array (for example ["event_id","event_date","event_type","source",...]).
-- The shape tables hold every standard column of a shape, but a given ERW table
-- may use only some of them (news_index has no parties, mw or price), and may
-- have its own columns in `extra` that are empty on every row. With this list a
-- reader (erw.SupabaseBackend, the site) returns exactly the table's columns.
-- Null for tables not in the live set.

alter table public.catalogue add column if not exists columns text;
