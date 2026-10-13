-- Energy Research Warehouse (ERW): the rollback of migration 032 (session 250). It lives in rollbacks/, not in
-- migrations/, so that apply.py's full run and its --only never pick it up; it is applied by name, by a person:
--
--     python warehouse/supabase/apply.py --rollback 032
--
-- It drops the index series_carbon_hourly_since. No row is deleted. The emissions page's read of the hourly carbon
-- table goes back to the primary key (about a second a page with 430 days in the live set). Safe to run again.

drop index if exists public.series_carbon_hourly_since;
