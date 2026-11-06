# The Section 1603 grants, one row an award (U.S. Department of the Treasury, the awardee list as of 1 March 2018)

Energy Research Warehouse (ERW), method note written in session 2116 (chain 069) for a table first written on 23 October 2026 (session 2112).

Tables: `treasury_1603_awards`

## Publisher and address

U.S. Department of the Treasury, Section 1603 Program, "Payments for Specified Energy Property in Lieu of Tax Credits": the awardee list, an Excel workbook linked from the program page,

`https://home.treasury.gov/policy-issues/financial-markets-financial-institutions-and-fiscal-service/1603-program-payments-for-specified-energy-property-in-lieu-of-tax-credits`

whose one "awarded" link was, for the run of 23 October 2026,

`https://home.treasury.gov/system/files/216/Website-Awarded-as-of-3.1.18.xlsx`

The User-Agent is "Mozilla/5.0 (compatible; ERW-connector/0.1; +https://github.com/SamuelEnrique/erw)". Source id `treasury:section_1603_awards`. Connector: `warehouse/connectors/treasury_1603.py` (session 2112), its only table. home.treasury.gov's robots file allows `/` (the docstring; session 2112 asked it in a call of its own).

The table is not scheduled: no line of `warehouse/run_daily.sh`, the other `warehouse/*.sh` scripts, `scripts/` or `.github/workflows/` names the connector (searched in session 2116), and `run_status.csv` holds no row for it. It was written once, by run `20261023T223300Z` on the data machine.

## Vintage and revision

The list's title gives "Awardees as of March 1, 2018" (`x_as_of` 2018-03-01); the award dates run from 1 September 2009 to 10 November 2017. The list was retrieved at 2026-10-23T22:30:27Z by the session's probe and reused by the write run (the header's "the list retrieved" time; the events shape has no `retrieved_at` column). Each run writes the whole table again (`ip.write_snapshot`); a later list would replace every row. `coverage.csv` gives the same 10,012 rows and the same first and last dates.

## Shape and variables

Events, 10,012 rows, one an award. `event_id` `treasury_1603:<the first 12 hex digits of a SHA-1 of the business, state, technology, amount and date>`, so it is stable; `event_date` the award date; `event_type` `grant_award`; `parties` the business as the Treasury names it; `entity_ids` `US-<state or territory>`; `mw`, `price` and `currency` empty (the list gives no capacity, and an award is not a price per MWh); `status` `awarded`; `x_state` (54: the 50 states, DC, PR, GU and VI); `x_technology` as the Treasury names it (19 names); `x_funded_usd` the amount funded, whole dollars; `x_as_of`.

The awards sum to USD 26,157,401,498. The median award is USD 85,030 (85,029.5), the mean USD 2,612,605; the largest is USD 513,753,359 (Arizona Solar One LLC, AZ, Solar Electricity, 4 March 2014), the smallest USD 217 (Sentry Security Systems, LLC, NH, Solar Electricity, 23 March 2012).

| Technology (as named) | Awards | USD million funded | Median award, USD |
|---|---|---|---|
| Wind | 434 | 12,894.4 | 9,765,030 |
| Solar Electricity | 8,050 | 9,562.6 | 83,538 |
| Biomass (open loop, cellulosic) | 61 | 940.9 | 5,378,717 |
| Geothermal Electricity | 22 | 719.6 | 22,816,839 |
| Solar Thermal | 482 | 696.8 | 26,399 |
| Hydropower (incremental) | 44 | 509.4 | 1,828,155 |
| Fuel Cell | 62 | 227.8 | 761,053 |
| Landfill Gas | 63 | 214.5 | 1,461,104 |
| Biomass (open loop, livestock) | 98 | 119.1 | 854,787 |
| Trash Facility | 34 | 93.5 | 1,498,978 |
| Small Wind | 480 | 82.0 | 47,024 |
| Geothermal | 6 | 26.5 | 1,164,886 |
| Hydropower (dam) | 13 | 22.5 | 632,403 |
| Combined Heat & Power | 52 | 18.0 | 138,232 |
| Geothermal Heat Pump | 90 | 16.2 | 48,351 |
| Marine | 10 | 10.1 | 356,518 |
| Biomass (closed loop) | 3 | 2.0 | 129,180 |
| Microturbine | 6 | 1.4 | 92,548 |
| Solar Lighting | 2 | 0.1 | 43,008 |

| Award year | Awards | USD million funded | of which Wind | of which Solar Electricity |
|---|---|---|---|---|
| 2009 | 148 | 1,658.2 | 1,575.0 (27 awards) | 22.7 (89) |
| 2010 | 1,407 | 3,138.9 | 2,703.9 (98) | 321.3 (1,060) |
| 2011 | 2,588 | 4,204.5 | 3,104.2 (120) | 770.5 (2,169) |
| 2012 | 4,036 | 6,395.6 | 3,616.3 (132) | 2,127.3 (3,273) |
| 2013 | 1,107 | 3,950.1 | 1,895.0 (56) | 1,525.8 (888) |
| 2014 | 425 | 4,306.0 | none | 2,364.5 (307) |
| 2015 | 165 | 1,425.2 | none | 1,372.2 (140) |
| 2016 | 59 | 547.2 | none | 541.9 (55) |
| 2017 | 77 | 531.7 | 0.02 (1) | 516.3 (69) |

By state, California took USD 7,045.6 million, Texas 1,993.1, Arizona 1,444.6, Illinois 1,260.2 and Nevada 1,069.9; New Jersey had the most awards (1,550), then California (1,335) and Pennsylvania (822). Solar Thermal's USD 538.8 million in 2014 is most of its total. The counts were computed in session 2116 from the rows, read past the 10 header lines; no `event_id` is given twice, and every `entity_ids` is `US-` with the row's `x_state`.

## Checks the connector makes

- Before any request, home.treasury.gov is checked against `warehouse/metadata/paused_sources.csv` by connector and by host; a paused publisher stops the run with no request. It is not paused.
- The program page must link exactly one awardee list (an `.xlsx` whose address holds "awarded"), or the run stops.
- The sheet's first cell must name "Awardees as of <date>", and one row must read Business Name, State, Technology, Funded, Award Date. A state that is not two capital letters, a funded amount that is not a whole number of dollars, a date that does not read, an award given twice (all five fields), two awards sharing an `event_id`, or no Total row stops the run, and nothing is written. Blank rows are passed over.
- The awards must sum to the Total row exactly.
- An award date the file holds as an Excel serial number (between 30,000 and 60,000) is read as one and listed in the header: one, row 7558, Shemron Properties LLC, NY, 40940, read as 1 February 2012. Nothing is filled.
- Ceiling: two requests a run (the page and the list), by the code's shape rather than a counter. Each address is tried up to four times, 5, 10 and 15 seconds apart (`ip.with_retries`); an HTTP 404 is not retried. One second after each request.

## The cross-check

Session 2112's cross-check is the connector's own: the awards sum to the list's Total row exactly (USD 26,157,401,498), and the program page reports "over $26 billion". The page counts "109,766 clean energy projects" while the list holds 10,012 awards, since an award can cover several projects; the header says so. There is no `runs/c069/s2112/cross.py`: that folder holds the probe, the trial, the test and the write, not a cross-check script.

## License

Not settled. The header: "License: not settled (the Treasury's site states no terms of reuse; see license_verdicts.csv). Cite the U.S. Department of the Treasury." Session 2111 read home.treasury.gov's robots file and its two notices (reads 265 to 267 of `license_reads.csv`) and found no terms of reuse and no copyright statement; the question of whether a federal work that states no terms is public is under session 2111's "For Samuel's ruling". `docs/licenses.md` gives "not settled (needs written permission by default)", the Treasury "not read", and the ERW verdict unsettled. Session 2112's report: the table is held from the Stanford draft and the release until a ruling, and is in the live set's catalogue hold and the release's storage hold.

Since session 2116 the header reads: "License: not settled (the Treasury's site states no terms of reuse, session 2111; no verdict yet), held internal until a ruling. Cite the U.S. Department of the Treasury."

## Found while writing this note

- `coverage.csv` gives the table the license flag `public`. The header's "License: not settled" is not one of the two words `build_coverage.py` reads (`public` or `internal`), so the flag falls to the source registry, whose "not settled" is not `internal`, and the builder writes `public`. `docs/licenses.md` shows the same disagreement (flag public, verdict unsettled).
- The docstring and the header say "see license_verdicts.csv", but `license_verdicts.csv` holds no row for the Treasury.
- The docstring says the page and the list are "saved in warehouse/raw/treasury_1603/ and reused offline". The code calls `ip.fetch_raw` without `fresh`, which reuses a saved copy on every run, offline or not, so a later run reads the saved page and list again and would not see a newer list.
- `coverage.csv`'s `source_report` for this table is "1 outlets", the coverage builder's wording for every events table, not the source id.
**Acted on in session 2116:** the connector now asks for its documents again unless `--offline` (`fresh=not args.offline`), so a later run sees a newer list; the source registry's license word is now `internal` until a ruling, so `coverage.csv` flags the table internal and it left the release package and its storage hold; the header no longer points to a verdict row that does not exist. `source_report` stays the builder's wording for events tables. The table was written again offline.

## What it does not hold

- Capacity (MW) and the projects inside an award: the list gives neither.
- Awards after the list's date, 1 March 2018.
- The tax credits taken by projects that did not take a 1603 payment.
