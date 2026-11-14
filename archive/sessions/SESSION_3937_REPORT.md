# Session 3937 report: the large-load research pass as three tables

Energy Research Warehouse (ERW). Chain 267, data machine (lab-desktop), 14 November 2026, 10:46 to 10:57 UTC. Opus 5.5. Model spend USD 0. Requests: Redivis's API only (one `--tables` run); no publisher asked (the connector reads committed files).

## What was built (`docs/state/data_requests_large_load.md` rows 1, 15 and 16)

- **`warehouse/connectors/large_load_research.py`:** reads `docs/research/large_load/utilities_2026-11-13.csv`, `changes_2026-11-13.csv` and `legislation_2026-11-13.csv` (window P4, sessions 5300 to 5304) and writes three events tables. No request, no model call. A row missing what it must hold (unique id, license `public` or `internal`, an http source, a read date, a rule status of the six, a change date) stops the whole write.
- **`utility_large_load_rules`:** 100 of 122 rows written, 22 held for a license (named in the header). 2 public rows have cells withheld by their `internal_fields` (`x_withheld`); 11 rows keep a registry pointer in `x_held` in place of the value.
- **`utility_large_load_rule_changes`:** 94 of 98 written, 4 held. Seven changes print a month only: kept as printed in `x_date`, dated by the day read (`x_date_kind`).
- **`state_large_load_laws`:** 27 of 28 written, 1 held (Indiana HEA 1007, IN.gov's terms).
- **`mw` empty in all three:** every size is a phrase (`x_threshold_mw`).
- **Under the data lock:** written, validated (all three PASS), archived (100, 94 and 27 rows), in coverage. A tier rule (`model_extracted`: AI research sessions, every cite matched by code) and a sector rule (`power;datacenters`) in `build_coverage.py`.
- **The records:** `licenses.py tables`, `check` (0 problems), `write`, `status`; `release_v1.py` (the three held out of v1: their ERW verdict is unsettled, as the registry tables' is; the count line "54 tables of the public draft are held out"); `build_tables.py`; `build_llms.py`; the Redivis draft (100, 94, 27 rows; `erw_headers` 2,843 lines; nothing released).
- **The method:** `docs/methods/large_load_research.md`. **Test 3937** (6 tests). Tests 1008, 203, 237, 238, 275, 378, 410, 469, 505, 53, 67 with 3937 and 2924: 139 passed.
- **Not loaded into the live set:** not in `live_set.yaml`; no page reads them yet.

## The registry corrections (rows 2 to 13), 11:17 to 11:29 UTC

Every value from the research pass's own cites (no document read again, no request):

- **Row 8, its default applied (a tightening):** fourteen tariff files held internal under ruling 4 (hosts whose terms bar automated reading or reproduction, or IN.gov's): the three Entergy schedules, Dominion's GS-4, CenterPoint Houston, SRP's E-67, Georgia Power, Alabama Power, APS, Oncor's two, PG&E's B-20 and I&M's two.
- **A fault found:** the tariffs connector merged into the old table, so held schedules' rows stayed (42 kept). It now writes the filed rows whole from the registry and keeps only the other connectors' (OpenEI) rows.
- **Row 2:** NV Energy's file now cites the form LLESA itself (proposed, PUCN Docket 26-05007, filed 7 May 2026): 90 percent minimum, ten-year term, security within 15 business days, the termination payment.
- **Row 5:** Dominion's GS-5, a new file, from the Florida PSC's copy of the SCC's Final Order (ordered, effective 1 January 2027; 25 MW, 85 percent, 14 years, USD 1.5 million a MW; appeal pending).
- **Row 7:** Duke's automatic extension, the letter of credit's ratable reduction, the security and the liquidated damages.
- **Row 9:** PGE's Schedule 96 effective 8 July 2026 (Order 26-239), with the system capacity allocation deposit in the notes.
- **Row 10:** Xcel Colorado's 15-year term read in PSCo's 10-Q and the CPUC's page (notes; still proposed). A first edit broke the YAML with inner double quotes; fixed in the next commit before any build.
- **Row 11:** AEP Ohio's DCT as the PUCO's order of 9 July 2025 adopts it, a new public file from the Florida PSC's copy; the tariff book's file stays held.
- **Row 12:** Ameren's and Evergy's collateral exemptions (60, 50, 40, 25 percent, capped at USD 175, 150, 125, 75 million).
- **Rows 3, 4, 6:** Oncor's docket, I&M's collateral timing and SRP's 15-year term recorded in their (held) files.
- **Row 13:** the method's Waiting entry for 16 TAC 25.194 now names the PUCT's adoption order and its steps. Not written to the registry while the licensing sweep's PUCT hold stands.
- **The table:** `utility_large_load_tariffs` 95 to 60 rows (31 schedules, 15 utilities, 15 held), validated, archived, in coverage, on the Redivis draft (twice: after row 8, then after the edits).

## Not done here

- **Row 14** (PG&E's Rule 30 re-cited to the CPUC's Decision 25-07-039) and **row 17** (the operator documents that changed: FERC's acceptance of PJM's definition, the PUCT's Batch Zero order, the PA PUC's closed date, Utah's amendments under comment; the CAISO Board's decision is done in session 3927): carried to file 272.

## Decisions made without you

- **One public table per dataset, held rows not written,** as `utility_large_load_tariffs` holds its schedules (ruling 4), in place of a second internal table per dataset.
- **The three tables are on test 4101's list** of public tables whose publisher has no single verdict (session 3938), beside `utility_large_load_tariffs` and `large_load_connection_rules`, on ruling 4's reasoning.

## For Samuel's ruling

- **Row 8's default was applied:** fourteen tariff files held internal (the default its row states, and ruling 4's own rule). Default kept; each is public again once re-read from a commission's copy.
- **16 TAC 25.194's steps** (ERCOT's time to connect, from the PUCT's own adoption order) wait for your ruling on the PUCT's link policy. Default: not in the registry.

- **The three research tables are flagged public under ruling 4** (each written row a commission's copy, a filed tariff book, an SEC filing, a grid operator's posted document or a legislature's text). Default: public, out of release v1 while their verdict is unsettled. If you rule otherwise, their header's license line turns them internal on the next write.
