# SESSION 39: Three more events on the template

## Read first
archive/sessions/SESSION_36B_REPORT.md and SESSION_36C_REPORT.md,
warehouse/derived/event_window.py, docs/methods/events.md, the /events pages, the saved
per-BA extracts (demand and CO2 from 2018-07-01), ercot_all_hub_prices_history.

## Budget and rules
- Expected Anthropic API spend: USD 0. Hard cap: USD 0. No model calls.
- No pulls. Reading primary-source web pages as text for framing is allowed; nothing
  from them is stored as data.
- One event at a time, one commit each. Supabase: this table only, within 350 MB.
- The daily job may land: pull and merge before pushing, never force push.
- Every claim in a framing sentence carries a primary source whose text states it
  (ISO, EIA, FERC, NERC, a state agency); where none is found, drop the claim.

## Events (same key, same weekday-aligned baseline 364 and 728 days earlier, both held)
1. `caiso_heat_2020`: CAISO, 2020-08-10 to 2020-08-24; demand served, hourly max,
   carbon intensity, vs baseline. CAISO prices for 2020 are not held: the page says so.
   Framing from CAISO's Final Root Cause Analysis (already cited on /grid/caiso).
2. `elliott_2022`: PJM, MISO, SPP, NYISO, ISO-NE, ERCOT, 2022-12-19 to 2022-12-29;
   demand and intensity per grid, ERCOT hub prices. PJM prices stay internal. Framing
   from PJM's Elliott report and FERC and NERC's joint inquiry report.
3. `ercot_heat_2023`: ERCOT, 2023-08-01 to 2023-09-10; demand, hourly max, intensity,
   hub real-time and day-ahead daily mean and max. Framing: find ERCOT's own release for
   the September 6, 2023 energy emergency and its demand records; cite only what the
   text states.
For each: the deepest or highest day against baseline as a row, and a page
/events/<slug> on the COVID pattern (one comparison chart, small multiples where more
than one grid, one headline line per grid read from the table). Where a finding
contradicts the headline story, say so as 36B and 36C did.

## /events index
Four to five cards, one per event, each with its dates, grids, and one headline number
read from the table with its check key.

## Verify and ship
Validator, coverage, archive, Supabase, Redivis draft upload, llms.txt and the chat
catalogue, check-routes and check-values, tests/, deploy, live checks.

## Do not
No pulls, no model calls, no new tables, no deletions from Redivis, no force push.

## Report: archive/sessions/SESSION_39_REPORT.md
Per event: rows, headline figures with rows, sources for every framing claim, what
contradicted the story. Supabase before and after. Run health, and whether the 14:00 UTC
daily run landed and passed (the gate). Decisions made without a human, open questions,
wall time, spend USD 0 confirmed. Commit after every event. Push. Stop.