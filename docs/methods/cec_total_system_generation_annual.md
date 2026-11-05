# California's in-state generation, imports and total system power by fuel, a year (California Energy Commission, Total System Electric Generation)

Energy Research Warehouse (ERW), method note written in session 2116 (chain 069) for a table first written on 23 October 2026 (session 2109).

Tables: `cec_total_system_generation_annual`

## Publisher and address

California Energy Commission (CEC), Energy Almanac, the workbook "Total System Electric Generation 2009 to 2025 with totals" (posted October 2026). The connector reads the download page,

`https://www.energy.ca.gov/media/7311`

and takes from it the one link to a Total System Electric Generation workbook, which was, for the run of 23 October 2026,

`https://www.energy.ca.gov/sites/default/files/2026-10/Total_System_Electric_Generation_2009-2025_with_totals_ada.xlsx`

The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `cec:total_system_electric_generation`. Connector: `warehouse/connectors/cec_total_system.py` (session 2109), its only table. The Commission's robots file disallows `/core/`, `/profiles/`, `/search/`, `/admin/` and the user pages, not `/media/` or `/sites/default/files/` (the docstring); session 2109 asked it in a call of its own.

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `scripts/` or `.github/workflows/` names the connector (searched in session 2116), and `run_status.csv` holds no row for it. It was written once, by run `20261023T214724Z` on the data machine.

## Vintage and revision

Years 2009 to 2025 (`ts_utc` 1 January). The workbook was retrieved at 2026-10-23T21:44:27Z by the session's probe and reused by the trials and the write run; its Last-Modified, the rows' `vintage`, is 2026-10-07T22:24:36Z. The Energy Almanac's latest yearly page is still 2024's; 2025 is kept as the workbook gives it (session 2109's decision). `coverage.csv` gives the same 795 rows, 47 entities and the same first and last `ts_utc`.

Each run writes the whole table again (`ip.write_snapshot`); a later workbook replaces every row.

## Shape and variables

Series, 795 rows, 47 series. `entity` `cec_tsp:<region>:<fuel>`; `variable` `in_state_generation` (region california, 12 fuels), `imports` (northwest and southwest, 12 fuels each) or `total_system_power` (region total, 11 fuels: oil and other combined as `oil_other`, and `unspecified_imports`); `unit` MWh (the Commission's GWh times 1,000); `freq` P1Y; `geo` US-CA; `market` empty; `node` the region and fuel as the workbook names them; `x_region`; `x_fuel`.

| Variable | Series | Rows | Mean MWh | Lowest | Highest |
|---|---|---|---|---|---|
| `in_state_generation` | 12 | 204 | 16,830,721 | 0 (18 rows: `california:unspecified` in all 17 years, `california:other` in 2010) | 122,005,000 (`california:natural_gas`, 2014) |
| `imports` | 24 | 404 | 3,590,531 | 0 (90 rows, `northwest:coal` in 2014 among them) | 34,535,000 (`southwest:unspecified`, 2009) |
| `total_system_power` | 11 | 187 | 26,117,864 | 49,000 (`total:oil_other`, 2011) | 132,157,000 (`total:natural_gas`, 2014) |

Forty-three series hold all 17 years; four hold 16 (`northwest:oil`, `northwest:other`, `southwest:oil`, `southwest:other`), the four 2025 cells the Commission writes as a dash (three) or leaves blank (one), as the header lists them. Summed over fuels, in-state generation was 205,698 GWh in 2025 (the most, 216,181, in 2024), imports 61,963 GWh (the most, 102,865, in 2012) and total system power 267,660 GWh (the most, 301,965, in 2012). In 2025 in-state solar was 55,528 GWh and natural gas 74,316; in the total system solar was 66,459 and natural gas 81,319. The counts were computed in session 2116 from the rows, read past the 10 header lines; no (entity, variable, ts_utc) is given twice.

## Checks the connector makes

- Before any request, the Commission is checked against `warehouse/metadata/paused_sources.csv` by connector and by host; a paused publisher stops the run with no request. It is not paused.
- The download page must link exactly one Total System Electric Generation workbook, or the run stops.
- The sheet must hold one header row "Region", "Fuel Type" with a run of years; a region or fuel not in the map, a region and fuel given twice, a cell that is not a number (other than a dash or a blank), a total row missing, or a key given twice stops the run, and nothing is written.
- Each region's fuels must sum to its total row, Northwest and Southwest to Total Imports, each fuel of the Total block to the three regions' (oil and other together), and the Total block to the Grand Total, within 1 GWh. The total rows are checked and not kept.
- A cell written as a dash or left blank has no row and is listed in the header; the Total block's empty row and the workbook's note ("All figures are gigawatt-hours") are passed over. Nothing is filled.
- Ceiling: two requests a run (the page and the workbook), by the code's shape rather than a counter. Each address is tried up to four times, 5, 10 and 15 seconds apart (`ip.with_retries`); an HTTP 404 is not retried. One second after each request.

## The cross-check

Session 2109 set in-state generation against EIA's California net generation summed to the year (`eia_state_generation_monthly`, all sectors, full years) in `runs/c069/s2109/cross.py` (on the data machine, not in git). The ratio is 0.985 to 1.012 in every year from 2009 to 2025, and in 2025 the fuels match closely (solar 1.012, wind 1.005, gas 1.000, nuclear 1.001, geothermal 1.001, coal 1.042); neither figure includes EIA's small-scale solar.

## License

The header: "License: the State of California's conditions of use (information on state websites is in general in the public domain); see license_verdicts.csv. Cite the California Energy Commission." Session 2109's report: the Commission then had no verdict of its own, and the header rests on the State's notice (read 10). Since session 2111 `license_verdicts.csv` gives the Commission its own verdict, "may be public", and "needs written permission" if the ERW sells anything (read 264: its materials are free for public use with credit to the Commission; commercial or profit-making use is prohibited). `docs/licenses.md` gives the ERW verdict public; `coverage.csv`: public; `sources.csv`: may be public. Session 2109's report holds the table in the live set's catalogue hold and the release's storage hold.

Since session 2116 the header reads: "License: may be public, noncommercial with credit (the Commission's Conditions of Use: its materials are free for public use crediting the Commission; commercial or profit-making use is prohibited; see license_verdicts.csv). Cite the California Energy Commission."

## Found while writing this note

- The docstring and the header name the State of California's conditions of use (read 10) as the table's license. `license_verdicts.csv` now holds the Commission's own verdict (read 264, session 2111), which adds that commercial or profit-making use is prohibited; the header does not say so.
- The docstring says the page and the workbook are "saved in warehouse/raw/cec_total_system/ and reused offline". The code calls `ip.fetch_raw` without `fresh`, which reuses a saved copy on every run, offline or not, so a later run reads the workbook of October 2026 again and does not find a newer one until the raw files are moved.
**Acted on in session 2116:** the connector now asks for its documents again unless `--offline` (`fresh=not args.offline`), so a later run sees a newer workbook; the docstring and the header now name the Commission's own verdict (read 264: noncommercial with credit), and the table was written again offline; the source registry's license word is now `public`.

## What it does not hold

- Small-scale (behind-the-meter) solar: not in the Commission's in-state generation.
- Months: the workbook is annual.
- The Commission's total rows (region totals, Total Imports, Grand Total): checked and not kept.
- Years before 2009.
