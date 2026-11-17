# The Flex Alert scorecard (`/grid/caiso/alerts`): cross-check against published figures, 16 November 2026

Energy Research Warehouse (ERW), session 7532 (chain 304, part A). The page's headline counts and one headline estimate
beside what the publishers themselves print. No figure of the page or of a table is adjusted to match. The method note
is [`docs/methods/caiso_alerts.md`](../methods/caiso_alerts.md); the faults are in
[`caiso-alerts-faults-2026-11-16.md`](caiso-alerts-faults-2026-11-16.md).

## What was read, and how

- **California ISO, "Grid Emergencies History Report (1998 to present)"**,
  `https://www.caiso.com/documents/grid-emergencies-history-report-1998-to-present.pdf`, revision date 10/09/2026
  (Last-Modified Fri, 09 Oct 2026 21:56:26 GMT), 196 pages, 1,048,832 bytes. One request on 16 November 2026, with the
  contact string "ERW research project, github.com/SamuelEnrique/erw". CAISO's robots file (read first, the same day)
  disallows `/resources/*` only and allows the rest; its Terms of Use allow use of its materials with copyright notices
  kept and the California ISO credited. Read: page 1 (the yearly day counts from May 2022), page 3 (the yearly day counts
  from 1998 to April 2022), and the record pages that name an EEA 2 of 2022 (pages 61, 66, 71, 72 and 77), with
  pdfplumber. The two summary tables, as read, are `replication/caiso_alerts/gehr_summary_2026-10-09.csv`, 2018 to 2026.
- **U.S. Energy Information Administration, "California consumers respond to appeals for electricity conservation
  during heat wave"**, Today in Energy, 28 September 2022, `https://www.eia.gov/todayinenergy/detail.php?id=54039`. The
  robots file of eia.gov (read first) does not disallow `/todayinenergy/`. One request.
- Not read: CAISO's summer assessments and its 2020 root cause analysis (the report above is CAISO's own list of every
  notice, and stands for the counts); the CPUC's Public Advocates Office analysis of September 2022 (its host answered
  no robots file, and the EIA article stands for the same evening); trade press.

## 1. The notices table, by year and kind, against CAISO's own counts

CAISO's summary tables count the days each kind of notice lasted. The warehouse's table (`caiso_grid_emergencies`, the
same revision, read 13 October 2026) counted the same way (distinct local days, any region), 2018 to 2026:
**66 of 71 year-kind counts equal** (`replication/caiso_alerts/crosscheck_rows.csv`). The five that differ:

| Year, kind | CAISO's summary | The table | Why |
|---|---|---|---|
| 2022, EEA 2 | 5 | 4 | CAISO's own record pages list EEA 2 on 4 days, 5 to 8 September 2022 (pages 61, 66, 71 and 77); the summary says 5. The table follows the records (faults, row 10). The page's notices cells show EEA 2 on those four days |
| 2018, transmission emergency | 2 | 1 | Recorded in the table's header since session 58; a kind the page does not show |
| 2019, transmission emergency | 3 | 2 | The same |
| 2022, transmission emergency | 10 | 11 | The same |
| 2020, Restricted Maintenance Operations | 20 | 18 | The same; RMO is not an alert day and the page does not show it |

Flex Alert days by year, CAISO and the table alike: 2018 2, 2019 1, 2020 10, 2021 8, 2022 11, 2023 0, 2024 0, 2025 0,
2026 0. EEA Watch: 2022 9, 2023 2, 2024 1, then none. EEA 1: 2022 6, 2023 1. EEA 3: 2022 1. Restricted Maintenance
Operations: 2025 2 and 2026 6 days, the only notices of those years with one transmission emergency in 2025.

## 2. The page's alert days by year against CAISO's counts

The page counts a day once whatever notices it carries, of the eleven alert kinds, for the whole area, and scores only
days with complete data. CAISO publishes no count of that union, so the nearest published figures stand beside it.

| Year | The page: alert days (`year_days`) | CAISO: Flex Alert days | CAISO: other alert-kind days | Difference, and why |
|---|---|---|---|---|
| 2018 | 2 | 2 | none | none |
| 2019 | 2 | 1 | Warning 1 | +1: 2019-07-28, a Warning with no Flex Alert, is an alert day by the method |
| 2020 | 11 | 10 | Alert 9, Warning 7, Stage 2 6, Stage 3 2, load interruption 1 | +1: 2020-08-15 (Stage 3, rotating outages, no Flex Alert) is an alert day. CAISO's 10 Flex Alert days count the one for 1 October under 30 September, the day it was issued; the page scores 1 October (faults, row 3) |
| 2021 | 8 | 8 | Warning 4, Stage 2 1 | Equal counts, different days: CAISO's include 2021-07-12, which the page does not score (incomplete data); the page's include 2021-07-29, a Warning only (faults, row 4) |
| 2022 | 11 | 11 | EEA Watch 9, EEA 1 6, EEA 2 5 (4 in the records), EEA 3 1 | none: every EEA day of 2022 also had a Flex Alert |
| 2023 | 3 | 0 | EEA Watch 2, EEA 1 1 | +3: the three days are EEA days with no Flex Alert (2023-07-20 EEA 1; 2023-07-25 and 2023-07-26 EEA Watch) |
| 2024 | 1 | 0 | EEA Watch 1 | +1: 2024-07-24, EEA Watch |
| 2025 | none (no row) | 0 | none | none: a true zero; the page now says the notices run to 2026-10-08 with no alert day after 2024-07-24 |
| 2026, to 8 October | none (no row) | 0 | none | none; the scorecard's sample ends 2025-10-31 |

Pooled: 38 scored alert days and 204 alert hours on the page; 39 by the rule from CAISO's notices.

## 3. The page's estimate for 6 September 2022 against the EIA's account of that evening

| Our figure | Ours | Published figure | Publisher, document, date | Difference | Why |
|---|---|---|---|---|---|
| The cut on 2022-09-06, mean over the alert hours 16:00 to 21:00 (`reduction_mw`) | -1,452.00 MW: demand served ran 1,452 MW above the model (interval -4,565.31 to 1,494.75 on the page) | "Within five minutes of the text alert, electricity demand in CAISO declined by more than 2,100 MW" from the hour-ahead forecast; "Electricity demand was consistently below the hour-ahead forecast until the demand response event ended at 9:00 p.m." | U.S. EIA, Today in Energy, 28 September 2022 | Opposite in sign, and not the same measure | The EIA measures five minutes after the 17:45 text against CAISO's hour-ahead forecast, made that afternoon with the day's conditions known. The page measures whole hours against a weather-and-calendar model fitted on other days. 2022-09-06 (98.78 F) is hotter than every day but one the model learned from (`train_days_as_hot` 1), where its error is largest. The two do not contradict each other: a large short drop inside an hour the model under-predicts can both hold. The page says hourly data blurs short cuts |
| The evening's demand, the hour 17:00 to 18:00 Pacific (`actual_mw`, PT1H, drawn in the day's chart) | 51,104 MW, the hour's mean; 16:00 to 17:00, 50,609 MW | "electricity demand in CAISO reached an all-time high of 51,426 megawatts (MW) at 4:55 p.m. on September 6, 2022" | U.S. EIA, the same article | 322 MW under the instant peak | An hour's mean is under its highest five minutes. EIA-930's hourly Demand is the series both are read from |
| The notices of 2022-09-06 (the notices cell) | EEA 1, EEA 2, EEA 3, EEA Watch, Flex Alert | "CAISO had already issued a Flex Alert asking Californians to conserve energy between 4:00 p.m. and 9:00 p.m."; "CAISO issued an Energy Emergency Alert Stage 3" | U.S. EIA, the same article | none; the page's alert hours are 16:00 to 21:00 | |

## 4. What stands against nothing

The pooled cut (-503.18 MW, interval -1,274.9 to 247.4), its MWh and percent, the value (USD -5.47 million over 19
hours) and the model's hot-day error (-239.34 MW over 128 days) are this scorecard's own and no published estimate
covers the same days, hours and counterfactual. CAISO and the state publish what programs were dispatched, not an
independent estimate of every alert day; the method says so (`flex_alert_scorecard.md`, section 1).
