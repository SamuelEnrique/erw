-- Energy Research Warehouse (ERW): Supabase live set, migration 032 (session 250).
--
-- The emissions page reads the hourly carbon intensity of every grid for the last week in one read
-- (site/app/emissions/page.tsx: table_name = 'carbon_intensity_hourly', ts_utc since seven days ago, in the key's
-- order, a thousand rows a page). Session 245 took the table in the live set from 35 days to 430 (12,700 rows to
-- 155,911). The planner answers that read from the primary key (table_name, entity, variable, ts_utc, event), which
-- gives the order for free but has to walk every hour of each balancing authority to find its last week: 0.96 s for
-- the first thousand rows on 13 October 2026, and more for the second and third, against the 3 s the site's key is
-- allowed. A cold or busy database then cancelled it ("canceling statement due to statement timeout"), the page drew
-- "no data" in two blocks, and the route check of three landings failed on it that night (sessions 235, 238, 249).
--
-- This index holds the table's rows by hour with every column the read selects, so the week is one short range read
-- from the index alone, then sorted. It is partial (this table only: about 156,000 of the 2.5 million rows of
-- series) and small. No page's query changes. Idempotent; the rollback drops it.

create index if not exists series_carbon_hourly_since
  on public.series (ts_utc) include (entity, variable, event, value, unit, freq)
  where table_name = 'carbon_intensity_hourly';

analyze public.series;
