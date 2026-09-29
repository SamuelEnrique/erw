-- Energy Research Warehouse (ERW): Supabase live set, migration 009 (session 29).
--
-- The partition column of the consolidated EIA-930 tables (docs/datastandard.md, decision 28:
-- partition keys are columns, never name suffixes). eia930_all_demand and eia930_all_generation
-- hold the eight balancing authorities that were eight tables each; ba names which one a row is
-- (ciso, erco, isne, miso, nyis, pjm, swpp, us48). Empty for every other table. The other
-- consolidated tables in the live set carry their partition in market, which series already has.
-- The ERCOT history's year column is not needed here: that table is not in the live set.

alter table public.series add column if not exists ba text;
