# Session 2448 report: the next file first; Rwanda's electricity a quarter, July 2021 to June 2024 (RURA's Electricity Statistics Reports)

24 October 2026, from 12:19 UTC, on lab-desktop (the data machine), the first session of `queue/done/118-day-18-november-data-rwanda-senegal-azerbaijan-uzbekistan.md`, unattended. Precheck passed (`runs/c118/pre2448.out`). Model spend USD 0. Pulls: 9 of 15 (below).

## Read these first

- **Chain 118 taken** at 12:19 UTC by chain 059's agent when chain 114 landed (ded5150f), under the owner's instruction for that run: run the file the queue step prints. Chains 115 and 117 run beside it under other agents, who were told.
- **The next file first,** pushed to main on its own before any other work (646847d5, with snapshots): `queue/next/119-day-19-november-data-kyrgyzstan-cote-divoire-jamaica-laos.md`, sessions 2462 to 2475, machine: data.
  - 119 and sessions 2462 to 2475 were free on main and on every branch.
  - Its sources are Kyrgyzstan (the National Statistical Committee), Côte d'Ivoire (CI-ENERGIES or ANARE-CI), Jamaica (the Office of Utilities Regulation or STATIN) and Laos (the Ministry of Energy and Mines or EDL). None is held, and chains 057 to 118 did not plan them.
  - It carries 118's rules, the hosts chains 114 and 117 closed, and test 378's rule on internal tables.
  - Chain 117's agent later reported that its session 2436 read stat.gov.kg: there is no robots file, and its open data for electricity covers 2015 to 2019 under CC BY-NC-SA 4.0. Chain 118's session 2461 will add this to file 119.
- **REG not taken:** its robots file did not answer within 60 seconds (read 810).
- **One internal table:** `rura_rwanda_electricity_quarterly`, 690 rows, 45 entities, July 2021 to June 2024. It is written, validated, archived, in coverage (sector power), and held from the live set. It comes from three of the Rwanda Utilities Regulatory Authority's quarterly Electricity Statistics Reports, each covering five quarters (reads 816 to 818 on this branch's numbering):
  - Table 1: each plant's generation, domestic generation, the regionally shared plants' share, imports and the total;
  - Table 3: electricity sold by customer category (exports and Nasho's own use among them) and the total sold;
  - in MWh (the reports' kWh divided by 1,000), a quarter.
- **Every check holds:**
  - the plants add to domestic generation, and domestic, regional shared and imports to the total, within 1 MWh;
  - the categories add to the total sold, within 1 MWh, where a total is printed;
  - the reports agree on all 2022 quarters that two of them give (0 values differ).
- **The September 2022 report's sales table has ten categories and no total,** nor street lights, Nasho's own use or exports. So Q3 and Q4 2021 have no `sales_total` and lack those three categories; the header says so.
- **Read with pdfplumber's tables, not the text layer,** whose cells shift between rows. Shema Power's 87 GWh in Q2 2024 (a methane plant; its capacity is in no saved file, and this line first said 56 MW, corrected in session 2452) and peat's 3.03% share agree with pdfplumber's rows and not with the text's.
- **Not taken:** the system peak demand, given only in a figure and the prose (233.74 MW in Q2 2024); the generation mix, given in percentages.
- **License: internal.** RURA's footer reads "© 2026 Rwanda Utilities Regulatory Authority", and its pages state no terms of reuse, so no verdict is recorded. `www.rura.rw`'s robots file disallows CMS paths and a long list of named crawlers, none of them this reader or an AI agent (read 811).
- **Test 205's bound raised by 40** for this chain's reads, which start at 763 on this branch.

## The cross-check (`runs/c118/s2448/cross.py`, `cross.out`; tables read past their header lines)

- **Total supply (domestic, regional shared and imports) against `owid_ember_electricity_annual`'s Rwanda demand:** 6.7 per cent above in 2022 (1.131 against 1.060 TWh) and 6.2 per cent above in 2023 (1.275 against 1.200 TWh). This report does not explain the gap.
- Electricity sold was 0.935 TWh in 2022 and 1.057 TWh in 2023, about 17 per cent below supply.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.reg.rw | 1 | robots (no answer in 60 s) |
| www.rura.rw | 8 | robots, the home page, the statistics pages (3), three reports (0.3 to 0.7 MB) |
| total | 9 of 15 | |

## Errors

- **The first parse stopped at the 2022 report's `0.0` values and its sales table without a total.** The reader takes decimals, and the sales sum is checked only where a total is printed.

## Decisions made without you

- **RURA's quarterly reports in place of REG,** whose host did not answer.
- **Three reports, July 2021 to June 2024,** within the ceiling.
- **The table internal** while RURA's terms are unstated.

## For Samuel's ruling

- **RURA's reports:** public or internal? It states no terms.

## Files

- New:
  - `warehouse/connectors/rura_rwanda.py`
  - `tests/test_session2448.py`
  - this report
- Changed:
  - `warehouse/metadata/build_coverage.py`, `warehouse/supabase/live_set.yaml`
  - `warehouse/metadata/license_reads.csv` (810 to 818), `license_tables.csv`, `docs/licenses.md`
  - `tests/test_session205.py` (the bound)
  - the coverage, sources and archive manifest files
- On the data machine only: `runs/c118/`, `runs/license_reads/s2448/`.
