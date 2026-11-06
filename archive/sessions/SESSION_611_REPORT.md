# Session 611 report: BOEM's offshore production by lease, from OGOR-A (OGOR-B read, not taken)

22 October 2026, from 01:30 UTC, on lab-desktop (the data machine), a session of `queue/done/037-night-22-october-sources.md`. Model spend USD 0.

## Read these first

- **New table `boem_ogor_lease_production_monthly`: 245,710 rows, 1,491 leases, January 2015 to June 2026.**
  - Oil (`kbbl`) and gas (`MMcf`) produced by each lease in the Gulf of America, a month.
  - The source is BOEM's OGOR-A well production files, one a year: each completion's monthly oil (barrels) and gas (thousand cubic feet), summed over the lease's completions and producing intervals.
  - Eleven 2024 rows have no lease number, only a unit agreement. They are kept under `boem_unit:<unit agreement>`.
  - A completion's reported zero is kept (71,425 zero rows). Nothing is filled. Water and injection volumes are not taken.
- **OGOR-B was read and not taken, as the chain file says.**
  - BOEM's yearly "description" PDF (2024: 1,163 pages) is a printed listing of the data, with no code meanings.
  - BOEM's field values page (`HtmlPage.aspx?page=ogorBFields`) names the 48 disposition codes: 01 "Sales - Subject to Royalty", 10 "Produced Into Facility", 11 "Transferred to Facility", 13 "Transferred from Facility", 14 "Injected On Lease", 21 and 22 flared, 61 and 62 vented, and so on.
  - It does not say which codes make a lease's production. Transfers and sales overlap, so a sum of codes would be my reading.
- **Cross-check against EIA's Federal Offshore Gulf of America series** (`eia_crude_production_state_monthly`, R3FM field production; `eia_gas_production_state_monthly`, R3FM gross withdrawals), all 138 months:
  - **Oil, 2015 to 2024**: BOEM over EIA from 1.000 to 1.004 (January 2024: 54,389 kbbl in both).
  - **Gas, 2015 to 2024**: from 0.999 to 1.006.
  - **2025 and 2026 drift**: oil from 0.987 to 1.031, gas up to 1.135 (May 2025). EIA's recent months are its estimates, revised later toward BOEM's reports; this reading is mine and is not checked.
- **Written under the data lock** (01:41 UTC) with `--offline` (0 requests). The validator, coverage `--only` and the archive exited 0 (245,710 rows archived). Release rows added; `licenses.py check` 0 problems: the table is public (BOEM, record 86, as BOEM's other three tables in the registry). **Held** from `/data` and Redivis v1. Sector rule `oil;gas`. Tests: `tests/test_session611.py`, 5.

## Decisions made without you

- **OGOR-A in OGOR-B's place.** The chain file asked for a lease's production and allowed it only if BOEM says plainly which numbers are production. BOEM defines OGOR-A's volumes as "the monthly quantity of oil [gas] produced from a completion", so the lease table comes from OGOR-A. OGOR-B's dispositions stay unread into the ERW.
- **The current year's file.** BOEM serves the current year as `ogoradelimit.zip`, with no year in the name. `ogora2026delimit.zip` answered an HTML page with HTTP 200. The connector asks for the no-year file for the current UTC year, checks that every file starts with a zip's `PK`, and stops if a file holds a month of another year.
- **Lease operators as `node`**: the operators BOEM names for the lease that month, joined by "; " (260 of 7,876 lease-months in 2024 had more than one).

## For Samuel's ruling

- Whether OGOR-B's dispositions (sales, flaring, venting, injection by lease) should come in. It would need a ruling on which codes count, or ONRR's reporter handbook read as the authority.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.data.boem.gov | 20 of 25 | the robots file (the same as session 605's, our agent not named), the 2024 OGOR-B PDF, the OGOR-A page, the two record layout pages, the OGOR-B code values page, the 2024 OGOR-A file (to read its form), the trial's 12 files, then the current year's file |

## Files

- New: `warehouse/connectors/boem_ogor.py`, `tests/test_session611.py`, this report. Changed: the sector rule, both holds, the release package, the license record, coverage and the archive manifest.
