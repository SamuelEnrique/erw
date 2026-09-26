-- Energy Research Warehouse (ERW): Supabase live set, migration 004 (session 13).
--
-- The SHA-256 of the rows load.py selected for each live-set table on its last
-- successful load (the table's license, then the selected rows as CSV). The next
-- load compares it with the SHA-256 of today's selection and skips a table whose
-- rows have not changed; the count reconciliation still runs for every table.
-- Null for tables not in the live set, and after a failed load of a table, so the
-- next run loads it again.

alter table public.catalogue add column if not exists rows_sha256 text;
