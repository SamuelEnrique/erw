# Session 109 report: the network, version 3, finished

**Done and on the live site, in review at `/network/v3`.** The approved pull was made: `eia930_daily_demand`, EIA's daily demand of every balancing authority since 2019, 190,512 rows of the 300,000 ceiling, USD 0. A replayed day now shows the grid's net imports as a share of its demand that day, and each supplier's share. Every control of `/network/v3` was rechecked in a browser, on this machine's build and on production: 30 of 30. The live page `/network` does not draw the replay and is unchanged. **Two deploys: the second put back a live methods page the first had added text to** (first point).

## Read these first

1. **A live page gained text it should not have, for about a quarter of an hour, and is back.** I wrote the method of the new share into `docs/methods/grid_network.md`. That file is the live methods page `/data/methods/grid_network`; the first deploy added 22 lines to it (the new section; no figure that was on the page moved). The comparison found it. The section now lives in version 3's own note, `docs/methods/grid_network_v3.md`, which is in review, and the live note is byte for byte what it was. The second deploy carried that. Its comparison is at the end of this report.
2. **On 15 February 2021, Texas imported 1.77 percent of its demand.** The replay now says so: ERCOT's demand that day averaged 50,152 MW; SPP supplied 779 MW of it (1.55 percent) and Mexico's CENACE 107 MW (0.21 percent). That is the number the replay could not give before: how little an island can lean on its neighbours on its worst day.
3. **A day's demand is used only inside a band, and 109 days are not.** EIA's daily demand is its own sum of the hours it holds, so a day with hours missing at the source can be far off. A day's demand is used when it is above zero and between half and twice the median of the six days around it (three before, three after); a day outside that carries no demand and shows no share. The band is wide on purpose: Texas's real fall in the storm stays in. It does not catch one impossible hour inside a day (PJM's 224,345 MW of 13 July 2020 adds about 4 percent to that day); the note says so.
4. **A share is of demand, not of supply, and not a contract.** The replay holds no generation by day. The page says what a share is: a neighbour's physical flow over the grid's demand, both as the day's average MW.

## The pull

`warehouse/connectors/eia930_daily_demand.py`, made on the pattern of session 68's daily interchange connector. EIA API v2, route `electricity/rto/daily-region-data`, type D, EIA's Eastern day. The connector asks the API how many rows the whole span holds before it pages, and stops if that passes the ceiling: EIA reported 190,512.

| | |
|---|---|
| Table | `eia930_daily_demand`, series, `demand_mwh`, entity `eia930:<BA>`, partition column `ba` |
| Rows | 190,512, of a ceiling of 300,000 |
| Span | 2019-01-01 to 2026-10-03, 71 respondents (balancing authorities and EIA's regions) |
| At or below zero | 8 rows, held as EIA gives them; the replay's band leaves them out |
| Requests | about 100 to `api.eia.gov` (a count, the newest day, and a month at a time), all saved under `warehouse/raw/eia930_daily_demand/` |
| Records | validator exit 0; in coverage (132 tables), the archive and the public Redivis draft; nothing released |
| Supabase | not loaded: a history, under `catalogue_hold`; its source held off `/terms`. The live set's rule for the recent EIA-930 tables no longer matches a table named `eia930_daily_...` |

**License: public domain.** EIA's terms (`https://www.eia.gov/about/copyrights_reuse.php`, read today): "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service." EIA asks for an acknowledgment; every row names its source.

## The replay

`warehouse/derived/network_daily.py` now puts each balancing authority's demand in each year's file, as the day's MWh over the hours of that Eastern day (24; 23 or 25 on the two days the clocks change): the day's average MW, the scale the flows are on. All eight years were rebuilt (`site/public/network/daily_2019.json` to `daily_2026.json`, and the index). 54 of the network's balancing authorities have a demand; 52 in every year to 2025.

On the page, for a replayed day and a chosen grid: "Net imports this day: 888 MW on average, 1.77 percent of its 50,152 MW demand", and in the list of who supplies it, each neighbour's flow with its percent of demand. A day whose demand is not used says "its demand for this day is not held" and gives no share. The live week is as it was (hourly demand of the seven ISOs).

## Every control of `/network/v3`, in a browser

`site/scripts/check-network-v3.mjs`, 30 checks, all passing on this machine's build and on production (in the internal view; a visitor gets the in-review page):

- **Opens** as the live week, prices off, nothing selected, a bare address; version 3's controls are there.
- **The replay:** the date picker loads a day of 2021 (a frame a day, 365 days); the moment reads as EIA's Eastern day; ERCOT's panel gives the day's net imports as the file has them; **the share of demand and each supplier's share are the file's** (new); **a day whose demand is not used gives no share** (new: LG&E, 4 March 2021); "Play the year" plays; a day of another year loads its own file.
- **The address** holds the view (the day, the grid, prices on, the trace) and a pasted address restores it.
- **Prices:** the switch draws a ring on each priced grid; the panel gives the day's hub price and the period's range; PJM says its prices are licensed.
- **Trace the power:** the suppliers of a grid, their shares summing to 100 and equal to the model's, and the sentence that these are physical flows, not contracts.
- **The live page `/network`** holds no date picker, no Prices switch, no trace, and leaves its address alone. Session 68's own browser test of it passes on production too.

## Every difference, the 25 live pages

| Comparison | Differences | What |
|---|---|---|
| `before-109` (22:10 UTC) against `after-109` (22:17), the first deploy | 54 | `/` 26: the 15-minute prices. `/network` 6: the hourly stamps. **`/data/methods/grid_network` 22: the new section. Not meant** |
| `before-109` against `after-109b` (22:31), after the second deploy | 32 | `/` 26: the 15-minute prices. `/network` 6: the hourly stamps. **`/data/methods/grid_network`: 0.** The other 22 pages: 0 |

## Tests and checks

- `tests/test_session109.py`, 9 tests: the connector asks for type D by Eastern day and counts before it pages; the table is held out of Supabase; the band on days made for the test (a day under half, a zero, a day over twice are not used; a real fall of a quarter is; nothing is filled); a day is its average MW over its own hours, the 23-hour day among them; the year's file equals the table over the day's hours for four grids (more than 1,400 days); the index says where demand comes from; the component's day view reads demand and shows a share only in the day view; the live page passes no version 3.
- Session 93's test of the year's file counts the new field.
- Every session's tests on this machine: 780 ran before the first push; one fails and is not this session's (the interchange ceiling).
- Both workflows passed (runs 37239022150 and 37239877707, merged as `8a8d62f` and `4ba3096`); Vercel accepted both deployments.

## Errors and decisions

1. **The method note went into a live page's file** (first point). The connector's docstring now points at version 3's note.
2. **The band for a day's demand is mine:** half to twice the median of the six days around it. Tighter would drop real days (a holiday, a storm); the hourly rule's 25 percent is for hours and does not carry over to days.
3. **The replay's files show MISO's daily hub price** where they did before this session (session 93 built them before the pause). I did not change that; it is in the state of the platform as a question for the pause.
4. **No model call. Model spend USD 0.00.** No force push. MISO stays paused: nothing was asked of it.

## For Samuel

1. **Version 3 is ready to be the live page as far as I can test it.** Session 93's report has the two edits that make it so. The one thing to decide first is MISO's price ring (third decision).
2. **The replay is built by hand.** One line in the daily run after `grid_network` would carry it forward; the daily demand connector is about 100 requests a run, or one month's worth if it is run monthly.

Energy Research Warehouse (ERW), session 109, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from about 21:50 to 22:35 UTC, unattended.

## The second deploy

`task/109-methods-back` (run 37239877707): the section moved to `docs/methods/grid_network_v3.md`, the live note restored. After it, the live methods page shows 0 differences against the snapshot taken before this session's first push; `/network/v3` and its own methods page render in the internal view on production and are closed to a visitor.
