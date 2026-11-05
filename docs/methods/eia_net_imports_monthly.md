# U.S. net imports of crude oil and petroleum products by partner, a month, January 2010 to July 2026: crude oil, total petroleum products and the two together, by country, the world and three groups (EIA, Petroleum Supply Monthly)

Energy Research Warehouse (ERW), method note written in session 2415 (chain 114) for a table first written on 24 October 2026 (session 2412 of chain 114, its report `archive/sessions/SESSION_2412_REPORT.md`).

Tables: `eia_net_imports_monthly`

## Publisher and address

U.S. Energy Information Administration (EIA), Petroleum Supply Monthly, U.S. net imports by country, through EIA's API v2, route `petroleum/move/neti`. The route's metadata (`runs/c114/s2412/meta_neti.json`) gives the monthly and annual frequencies, the facets duoarea, product, process and series, and the months 1920-01 to 2026-07. The header's page is `https://www.eia.gov/dnav/pet/pet_move_neti_a_ep00_imn_mbblpd_m.htm`; the access line is `https://api.eia.gov/v2/petroleum/move/neti/data/?frequency=monthly&data[]=value&facets[product][]=EP00&facets[product][]=EPC0&facets[product][]=EPP0&start=2010-01`, pages of 5,000 sorted by period and series.

| Product | EIA's product name | Variable | Unit as EIA gives it |
|---|---|---|---|
| EP00 | Crude Oil and Petroleum Products | net_imports_crude_and_products | MBBL/D |
| EPC0 | Crude Oil | net_imports_crude | MBBL/D |
| EPP0 | Total Petroleum Products | net_imports_products | MBBL/D |

Every record has the process IMN, "Net Imports". Source id `eia:petroleum/move/neti`. EIA's answer holds 65,501 records (its `total`), every one with a value and every one in MBBL/D. The 14 pages are saved in `warehouse/raw/eia_net_imports/20261024T104249Z/` (13 of 5,000 records and one of 501, served from 2026-10-24T10:42:54Z to 10:43:50Z, 1,657,684 to 1,670,071 bytes for the full pages and 168,660 for the last, without a Last-Modified). The URLs in `manifest.csv` there, and the table's `source_url`, write the API key as `REDACTED`. A one-month sample (`runs/c114/s2412/sample_neti.json`, May 2025) has 1,751 records over 43 products, all process IMN; EP00 has 143 partners in it, EPC0 45 and EPP0 142.

Session 2412 made 18 requests to api.eia.gov: the metadata and a month of `petroleum/pri/refoth` (`meta.json`, whose months end at 2022-03, and `sample.json`, which came back with a total of 0), the metadata and a month of `petroleum/move/neti`, and the 14 pages of the first trial. No page of EIA's was saved under `runs/license_reads/`.

Connector: `warehouse/connectors/eia_net_imports.py` (session 2412): `[--from 2010-01] [--offline | --fresh] [--out-dir DIR]` (the docstring's usage line omits `--out-dir`), at most 20 requests a run, 3 seconds apart; a page saved in `warehouse/raw` is reused unless `--fresh`. A process other than IMN, a product not asked for, a unit other than MBBL/D, a period that is not a month, a key given twice or a count of records other than EIA's total stops the run; a record without a number would have no row (there is none). Where a partner and month have all three products, crude oil plus products is compared with the total and the partner months off by more than 1 kbbl/d are listed in the run log; they do not stop the run. **No schedule runs it**: no step of `warehouse/run_daily.sh`, `warehouse/run_data_machine.sh`, `warehouse/run_data_machine_tables.sh`, `warehouse/run_monthly.sh`, `warehouse/refresh_supply.sh`, `warehouse/scheduled.py` or `.github/workflows/` names it. The table is public; it is held from the live set (listed under `catalogue_hold` in `warehouse/supabase/live_set.yaml`) and from the Redivis release (`STORAGE_HELD` in `warehouse/redivis/release_v1.py`).

## Vintage and revision

The first trial, run `20261024T104249Z`, fetched the 14 pages and stopped on the sum check ("24 partner months where crude oil plus products is not the total within 1.0 kbbl/d", its log in `runs/c114/s2412/trial/logs/`). The second trial (`20261024T104407Z`, `trial.out`: "0 requests") and the write, run `20261024T104444Z` ("File holds 65501 rows, one snapshot; the previous file held 0 rows"), read the saved pages ("raw file reused", 14 times in each log). `retrieved_at` is the time EIA served each row's page: 14 values from 2026-10-24T10:42:54Z to 10:43:50Z, 5,000 rows each and 501 for the last. `vintage` is blank. Header line 4, "Retrieved: 20261024T104444Z", is the write's run, not the retrieval.

EIA's records carry no preliminary or revision flag. A run replaces the whole file, but it reuses saved pages unless `--fresh`, so a revision reaches the table only on a run that asks the pages again.

## Shape and variables

Series, 65,501 rows, 530 entities `eia_net_imports:<series>` (EIA's series id, one a product and partner, as MCRNTUS2 for the world's crude oil), `unit` kbbl/d, `freq` P1M, `geo` US in every row, `market` blank, `node` EIA's series description (as "U.S. Net Imports from Canada of Crude Oil (Thousand Barrels per Day)"), `x_partner` 208 values.

| Variable | Series | Rows | Partners a month | Zeros | Negative |
|---|---|---|---|---|---|
| net_imports_crude_and_products | 208 | 28,828 | 132 to 158 | 10,390 | 11,710 |
| net_imports_crude | 114 | 8,061 | 23 to 56 | 100 | 2,683 |
| net_imports_products | 208 | 28,612 | 131 to 156 | 11,553 | 12,482 |

Every variable runs from January 2010 to July 2026 (199 months). Values are whole thousands of barrels a day (no figure has a fraction).

**Partners.** Of the 208 areas, four are the world (NUS-Z00, area name "U.S.") and EIA's groups OPEC (NUS-ME0), non-OPEC (NUS-MN0) and the Persian Gulf (NUS-MP0), each with the area name "NA"; the other 204 are countries and territories. 181 of them carry a three-letter area name, which `x_partner` keeps. 23 do not, and `x_partner` takes EIA's duoarea for them: 22 have the area name "NA" (among them Curacao NUS-NUC, 382 rows; Sint Maarten NUS-NNN, 366; Martinique NUS-NMB, 313; Serbia NUS-NRI, 144; Luxembourg NUS-NLU, 66; South Sudan, Burkina Faso, Laos, Palau and others) and the Midway Islands have "UMI-71" (NUS-NMQ, 24 rows, 2010). The three-letter names are EIA's: BUR is Burma, ANT the Netherlands Antilles (to October 2016, beside Curacao and Sint Maarten from May 2011; in 12 months both ANT and Curacao have a total other than 0), CXR is named "Kutubu, Christmas Island", and Puerto Rico (PRI) and the U.S. Virgin Islands (VIR) are partners in all 199 months.

**The groups.** OPEC plus non-OPEC equals the world within 1 kbbl/d in all 199 months for each of the three products. The files do not say which countries each group counts in a given month. The Persian Gulf has no crude oil record for July 2026 (nor has Saudi Arabia), while OPEC has 788 kbbl/d.

**Sign.** Imports less exports: a negative value is a net export to that partner. The world's crude oil and products together is negative in 75 of the 199 months, first in October 2019 (-440 kbbl/d) and in every month from October 2021; the most negative is May 2026 (-5,928).

Rows from the table (kbbl/d; a blank is a month without a record):

| Month | Partner | Crude oil | Products | Crude oil and products |
|---|---|---|---|---|
| January 2010 | World (NUS-Z00) | 8,459 | 944 | 9,404 |
| January 2010 | Canada | 1,840 | 508 | 2,348 |
| January 2010 | Mexico | 1,044 | -230 | 814 |
| January 2010 | OPEC (NUS-ME0) | 4,251 | 173 | 4,425 |
| January 2010 | Saudi Arabia | 958 | 5 | 963 |
| July 2026 | World (NUS-Z00) | 2,668 | -6,276 | -3,608 |
| July 2026 | Canada | 3,831 | 169 | 4,000 |
| July 2026 | Mexico | 352 | -869 | -518 |
| July 2026 | OPEC (NUS-ME0) | 788 | 99 | 888 |
| July 2026 | Saudi Arabia | | 21 | 21 |

## Placing values in time, and what is filled

`ts_utc` is the month's first day at 00:00:00Z, a label for the calendar month; values are the month's average a day. Nothing is filled.

**Absent records and zeros.** EIA answers "none" in two ways. For crude oil it mostly gives no record: of the 20,766 partner months with a total and a products record but no crude oil record, the total equals the products within 1 kbbl/d in 20,765 (2 kbbl/d in the other), so a missing crude oil record stands for no crude oil trade; only 100 crude oil rows are 0. For the products and the total it gives zeros: 11,553 product rows and 10,390 total rows are 0. 216 partner months have a total but no products record (215 of them with crude oil). Every total has its products or crude oil record, and no crude oil or products record is without a total.

**The sum check.** Crude oil plus products equals the total within 1 kbbl/d in 7,822 of the 7,846 partner months with all three. The other 24 are listed in the write's log, largest first: the Bahamas (NUS-NBF) October 2017, 46 kbbl/d; Curacao (NUS-NUC) March 2017, 37; India January 2015 and Malaysia December 2024, 22; Japan December 2024, 20; down to Malaysia and Peru in October 2017, 2. They are kept as EIA publishes them.

## License

Header: "License: public (a work of the U.S. government; cite "U.S. Energy Information Administration, Petroleum Supply Monthly")." `warehouse/metadata/license_verdicts.csv`: EIA, read 1 (EIA's copyrights and reuse page), "U.S. government publications are in the public domain and are not subject to copyright protection. You may use and/or distribute any of our data, files, databases, reports, graphs, charts, and other information products that are on our website or that you receive through our email distribution service.", verdict "may be public", if the ERW sells anything "may be public"; EIA asks for "Source: U.S. Energy Information Administration" with the date. `docs/licenses.md`, the table's row: verdict today "may be public", flag public, "agrees", ERW verdict public.

## Checks (session 2415)

The figures in this note were computed from the rows of `warehouse/output/eia_net_imports_monthly.csv`, read past its 10 header lines (counted), and from the 14 saved pages and the samples, read only (scripts run from the session's scratch folder, not saved under `runs/`).

- 65,501 rows and January 2010 to July 2026, as header lines 3 and 10 state; 530 series; no (entity, variable, ts_utc) twice; kbbl/d in every row.
- **Against EIA's pages:** the 65,501 records are the table's 65,501 rows, key for key, each value and each `node` EIA's, with 0 differences.
- **The groups:** OPEC plus non-OPEC against the world, all 199 months within 1 kbbl/d, each product.
- **The countries against the world** (crude oil and products together, the 204 partners that are not the world or a group): the signed median gap 1 kbbl/d, the median absolute gap 2, within 1 kbbl/d in 64 of 199 months and within 5 in 174; the largest July 2026 (the countries -3,499 against the world's -3,608, 109 kbbl/d), then June 2026 (33). Session 2412's cross-check counts only the 181 partners with a three-letter `x_partner`: the median gap 6 and the largest 120 kbbl/d (July 2026: -3,488).
- Session 2412's cross-check (`runs/c114/s2412/cross.py`, `cross.out`): the world's crude oil net imports against `eia_petroleum_snd_monthly`'s U.S. crude imports less exports, within 1 kbbl/d in all 139 months both hold (June 2025: 2,403 against 6,165 less 3,761, 2,404).

## The session report against the table

Every figure of `SESSION_2412_REPORT.md` checked against the table, EIA's pages and `cross.out` holds (65,501 rows, 530 series, January 2010 to July 2026, three of 43 products, kbbl/d, 7,822 of 7,846 partner months, 24 kept, Egypt in January 2010 at 16 kbbl/d, the Bahamas in October 2017 at 46, 14 pages, `refoth` ending in March 2022, `neti` to July 2026 and from 1920, 139 months within 1 kbbl/d, June 2025's 2,403 against 6,165 less 3,761, the median gap 6 and the largest 120, read 1, 18 requests), except:

- "The U.S. is a net exporter of crude oil and products together in December 2019 (-171 kbbl/d) and in July 2026 (-3,608 kbbl/d)": it is a net exporter in 75 of the 199 months, every month from October 2021 (point 2).
- "EIA's world total is kept; the table does not say what the gap holds": most of the gap is the 23 partners the cross-check leaves out (point 1).

## Limits

- **Partners overlap.** The world and the three groups hold the countries; a sum takes one level. The Netherlands Antilles is listed to October 2016 beside Curacao and Sint Maarten from May 2011, and the files do not say whether the figures overlap.
- **The U.S. of these figures does not include Puerto Rico or the U.S. Virgin Islands,** which EIA lists as partners.
- **A missing crude oil record means no crude oil trade,** by the totals, while the products and the totals carry explicit zeros.
- **The latest months are furthest from the world total** (109 kbbl/d in July 2026 with every partner summed); EIA gives no flag for a preliminary month.
- **The groups' membership** is EIA's and is not stated in the files.

## What it does not hold

- Months before 2010 (the route starts in 1920; `--from` asks them), EIA's 40 other products (the single products such as asphalt and road oil, as in the sample), gross imports or exports (`eia_petroleum_snd_monthly` holds the U.S. totals), annual figures, and U.S. states or districts.

## Points for the session to act on

1. **23 partners carry EIA's area code, not an ISO code, and the cross-check leaves them out.** Header line 2 says `x_partner` is "the partner's ISO 3166 alpha-3 code as EIA gives it, or EIA's area code for the world (NUS-Z00) and the groups". EIA gives the area name "NA" for 22 countries and territories (Curacao, 382 rows; Sint Maarten, 366; Martinique, 313; Serbia, 144; Luxembourg, 66; and 17 others) and "UMI-71" for the Midway Islands, so `x_partner` holds EIA's duoarea for them too. `runs/c114/s2412/cross.py` sums the countries with `x_partner.str.fullmatch(r"[A-Z]{3}")`, which leaves those 23 out; with them, the countries' gap to the world falls from a median 6 to 1 kbbl/d and the largest from 120 to 109 (July 2026). The header could say "or EIA's duoarea where EIA gives no three-letter code (the world, the three groups and 23 countries and territories)", and the report's gap should be restated from all 204 partners. The header could also name EIA's non-ISO codes (BUR for Burma, ANT for the Netherlands Antilles, listed to October 2016 beside Curacao and Sint Maarten).
2. **The U.S. is a net exporter in 75 months, not two.** The report says "The U.S. is a net exporter of crude oil and products together in December 2019 (-171 kbbl/d) and in July 2026 (-3,608 kbbl/d)". The world's total is negative in 75 of 199 months: first October 2019 (-440), all but seven months from then (the exceptions May and June 2020 and February, March, May, July and September 2021), every month from October 2021, and at its most negative in May 2026 (-5,928). The two months the report names are `cross.py`'s sample months.
3. **"EIA gives no record where it has none" holds for crude oil only.** The docstring and header line 3 say so. For crude oil a missing record stands for none (in 20,765 of the 20,766 partner months with a total and products but no crude oil, the total equals the products within 1 kbbl/d), but for the products and the total EIA gives a 0: 11,553 product rows and 10,390 total rows are 0, against 100 crude oil rows. A reader summing crude oil and products from the table should take a missing crude oil record as 0; the header could say so.
4. **Puerto Rico and the U.S. Virgin Islands are partners.** The docstring says "geo US (the importer)". EIA lists PRI and VIR as partners in all 199 months (VIR -63 kbbl/d in January 2025), so the importer is the U.S. without them. The header could say so.
5. **The usage line omits `--out-dir`.** The docstring's usage line is `[--from 2010-01] [--offline | --fresh]`; the connector also takes `--out-dir DIR`, which the trials used.

Compared besides, with no contradiction found: the header's and docstring's counts (65,501 records and rows, 7,822 of 7,846, 24 kept, the largest 46 kbbl/d for NUS-NBF in October 2017, the first Egypt in January 2010 at 16), "crude oil has 45 partners in May 2025, the products 142" (the sample), the three products and their names, the unit, the sign, the world and group codes, the overlap of the groups, "nothing is filled", `retrieved_at` against the raw manifest, the license lines, and every row against EIA's pages.

Acted on in session 2415: the docstring and header now say that 23 countries and territories carry EIA's area code in `x_partner`, as the world and the groups do; that Puerto Rico and the U.S. Virgin Islands are partners, so the importer is the U.S. without them; and that EIA gives no crude oil record where a partner has none but a 0 for products and the total. The usage line names `--out-dir`. Session 2412's cross-check now sums every partner but the world and the three groups (median gap 1 kbbl/d, the largest 109), and its report names the 75 months of net exports, every month from October 2021. The table was written again offline: the same rows.
