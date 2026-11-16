# Session 7002 report: the policy monitor's data faults (policy rows 5, 7, 12, 13, 15, 18, 25)

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0. Requests: the Federal Register's robots file read first (no rule touches the API or the printed texts; no AI agent named), then `policy_sources.py`'s daily sources and 115 printed texts (3.5 MB, one every two seconds, no HTTP 429).

## What a reader of `/policy?view=monitor` now sees that was wrong (the file rebuilt on the branch)

- **Dated steps:** 1,033 of 1,523 records hold them (514 in the file of 15 November; 61 at the review). The cause: 1,702 of 2,063 documents had their printed text read, on the runner that keeps no store, before the fields existed, and their fields came from the summary alone; the connector never asked again. Now 1,741 documents' fields are read from their texts.
  - Freeport (`ferc:CP26-551`): EA 2026-11-06 and decision deadline 2027-02-04 (no step before).
  - Amarillo (`ferc:CP26-581`): comments due 2026-12-02 (empty before).
  - FERC's draft policy statement (`ferc:PL26-3`): comments due 2026-11-16 (none before).
- **EPA's two actions of 17 September are two records:** the final partial repeal of the Carbon Pollution Standards (2060-AW55), effective 2026-11-16, now on the calendar; the proposed rescission (2060-AX00) with its hearing and comment dates. Before, one record drew the proposal's title with the final rule's impact sentence.
- **Each plain read names its document** (`plain_doc`: 35 of 292 are of an older document than the row draws), and **each significance its scoring document and why** (`significance_doc`, 1,512 records). The hovers are code rows (`docs/state/data_ready_c301.md` 5 and 6).

## Commits (on `wip/c301-data`)

- `ef3c63cc1` the code: `fields.HOUR_ETC` takes a time zone without "Time" ("by 5:00 p.m. Eastern on"); `policy_sources.read_texts` asks again, within its ceilings, a text marked read whose fields did not come from it, and keeps what it held when a ceiling leaves it; `records.group` splits a docket whose documents of one day carry different RINs; `monitor_site` writes `plain_doc` and `significance_doc`; `reads.years_beside_their_words` in `check_field`; test 7002 (10 tests: 8 fail on main's code, all pass here; the 280 tests of the policy modules pass, the graded thirty of `test_policy_records.py` included).
- `0a710ba33` `policy_actions` pulled again under the data lock (2,063 rows), validated, coverage `--only`, archived (1,752 rows new or changed), `site/data/policy/monitor.json` rebuilt.

## Each row's new state

- Row 5: not a fault now (`monitor.json` built 2026-11-15 by the daily run; rebuilt again).
- Rows 7, 12, 13, 18: fixed (`ef3c63cc1`, rebuild `0a710ba33`); rows 12 and 18's hovers in data_ready 5 and 6.
- Row 15: the data side fixed (row 7's steps); the page's "Comments closed <date>" in data_ready 7.
- Row 25: the check fixed; the BOEM read redone **needs the key** (one policy read, about USD 0.02).

## Needs the key

- Policy row 25: the BOEM read (`docket:BOEM-2023-0046`) redone, about USD 0.02. Until then the read stands as written.

## Decisions made without you

- **The RIN split only for the same day:** a first version split every docket with two RINs, and the graded thirty (`tests/test_policy_records.py`) failed on EPA's steam electric guidelines (2040-AG48 and 2040-AG41, phases of one rulemaking on different days). The rule now splits where two documents of one docket on one day carry different RINs, which is the review's case.
- **A record id of a split docket** is `docket:<id>.<RIN>` (data_ready row 8).
- **The year check** passes a year when the stem of the word before it in the read stands within 80 characters before the year in the source; common words (was, has, the ...) are not checked.

## For Samuel's ruling

- None new.
