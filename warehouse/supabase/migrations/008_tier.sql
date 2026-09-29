-- Energy Research Warehouse (ERW): Supabase live set, migration 008 (session 28).
--
-- The provenance tier of each table (coverage.csv, column tier; docs/datastandard.md,
-- "Provenance tiers"): source (as the publisher published it, reshaped only), derived
-- (computed by ERW code from other tables, method in docs/methods/) or model_extracted
-- (at least one column written by a model reading text). From Ben Domingue's review,
-- item 6: a user citing a number should know which kind it is.

alter table public.catalogue add column if not exists tier text;
