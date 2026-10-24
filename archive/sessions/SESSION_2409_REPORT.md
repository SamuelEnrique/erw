# Session 2409 report: Namibia not taken (NamPower reserves all rights, the ECB's certificate does not verify); Mauritius's electricity in its place, 2017 to 2025

24 October 2026, from 10:30 UTC, on lab-desktop (the data machine), the fourth session of `queue/done/114-day-15-november-data-paraguay-panama-guatemala-namibia.md`, unattended. Precheck passed (`runs/c114/pre2409.out`). Model spend USD 0. Pulls: 14 of 15 (below).

## Read these first

- **Namibia not taken:**
  - **NamPower:** its robots file allows the reader (read 666). Every page's footer reads "Copyright © NamPower, All Rights Reserved" (reads 667 and 668), and no terms of use or grant of reuse was found. New verdict, needs written permission (read 667), as chain 113 ruled for CNDC and ICE. Its annual reports were not fetched.
  - **The Electricity Control Board (www.ecb.org.na):** its certificate does not verify (`SSLCertVerificationError`, read 669). TLS verification was not bypassed and plain http was not tried, so nothing was read.
- **Two other replacements were closed on their robots file:**
  - El Salvador's Unidad de Transacciones answers HTTP 403 Access Denied from its CDN (read 670).
  - Honduras's system operator redirects to `cnd.enee.hn`, whose certificate does not verify (read 671).
- **In its place, one internal table:** `statsmu_mauritius_electricity_annual`, 79 rows, from Statistics Mauritius's "Energy and Water Statistics", the 2025 edition (Issue 1929, read 677) and the 2023 edition (Issue 1791, read 679). It is written, validated, archived, in coverage (sector power), and held from the live set:
  - Table 1, 2017 to 2025: electricity generated, the renewables' share, and electricity sold;
  - Table 7, 2022 to 2025: installed and effective capacity, and the peak demand of Mauritius and of Rodrigues (MW);
  - Table 8, 2022 to 2025: generation from hydro, wind, landfill gas, photovoltaic, gas turbines (kerosene), fuel oil and diesel, coal, and bagasse (the 2025 edition's "Bagasse & Fuelwood"), and the renewable total.
  - In MWh (the tables' GWh times 1,000) and MW.
  - Table 8's sources add to its primary, secondary and total rows, Table 7's to its total, and both totals equal Table 1's generation, within 0.01 GWh.
  - The two editions agree on every value both give (2018 to 2023).
- **License: internal, with a verdict of "may be public" (read 674), for your ruling.**
  - The Government of Mauritius's copyright notice lets State material be downloaded and reproduced accurately without specific permission, with the source (including the URL) and copyright status acknowledged.
  - "Any other proposed use" needs the Government Information Service's approval.
  - The table's header carries the acknowledgement. `statsmauritius.govmu.org` has no robots file (HTTP 404, read 672).
- **One request went to a guessed subject page** (read 675, HTTP 404). The two edition pages were found by a web search instead of more guesses.

## The cross-check (`runs/c114/s2409/cross.py`, `cross.out`; tables read past their header lines)

- **Generation against `owid_ember_electricity_annual`'s Mauritius demand:** within 0.6 per cent in every year from 2017 to 2024 (2024: 3.418 against 3.410 TWh).
- **The renewable total over generation** gives Table 1's renewables' share to one decimal in each year from 2022 to 2025.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.nampower.com.na | 3 | robots, the home page, the media page |
| www.ecb.org.na | 1 | robots (no response: certificate) |
| www.ut.com.sv | 1 | robots (403) |
| www.ods.org.hn | 1 | robots (redirected; no response: certificate) |
| statsmauritius.govmu.org | 8 | robots (404), the home page, the copyright notice, a guessed page (404), two edition pages, two workbooks |
| total | 14 of 15 | |

## Errors

- **The first parse missed Table 8's rows,** whose labels are indented across three columns. The reader now takes the first label among them.
- **Test 205 failed on the NamPower verdict,** first pointed at read 668, whose outcome carries a comment. It now points at read 667, the home page, whose footer carries the same sentence.

## Decisions made without you

- **No Namibian table** rather than one from a publisher reserving all rights, or a host whose certificate does not verify.
- **Mauritius in its place:** a statistics office with a written reuse notice, not planned by any chain (file 115 has Zambia, Botswana, Mongolia and Cambodia; file 117 has Tunisia, Egypt, Armenia and Nepal).
- **Two editions only,** within the ceiling: Tables 7 and 8 therefore start in 2022.
- **The table internal** until you rule on the notice.

## For Samuel's ruling

- **Statistics Mauritius's figures: public or internal?** Accurate reproduction with acknowledgement is allowed; "any other proposed use" needs approval.
- **NamPower's consent,** if Namibia's figures are wanted.

## Files

- New:
  - `warehouse/connectors/statsmu_mauritius.py`
  - `tests/test_session2409.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (666 to 679), `license_verdicts.csv` (Statistics Mauritius, NamPower), `license_tables.csv`, `docs/licenses.md`
  - the coverage, sources and archive manifest files
- On the data machine only: `runs/c114/s2409/`, `runs/license_reads/s2409/`.
