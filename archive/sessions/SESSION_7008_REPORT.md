# Session 7008 report: goal 2, the large-load waits brought current, their public summary and the utilities' dated totals

Energy Research Warehouse (ERW). Chain 301, data machine (lab-desktop), 16 November 2026. Opus 5.5. Model spend USD 0.

## The pull

- **Robots files read first, each in a call of its own:** NYISO, Grant County PUD, ERCOT and Bonneville answered 200 and no rule touches a path the connector reads (ERCOT disallows `/misapp` and `/misdownload`, never asked); the Internet Archive and Alberta's operator answered 404. No file names an AI agent.
- **Terms read again** (`--terms`): every sentence quoted of the Archive, Grant County PUD, ERCOT, Bonneville, Alberta and ISO New England stands word for word.
- **New copies:** NYISO's workbook; Bonneville's workbook (the connector had skipped its fixed address once saved, though Bonneville publishes again there: fixed, asked on every pull as NYISO's is); Alberta's lists of October and November 2026 (the connector took the newest month only: fixed, every month after the oldest held). Grant County PUD links the same file as on 9 October (30 July 2026); ERCOT's committee pages list no newer status report (the first try met a DNS failure; it answered on the second). The Archive's listings were not asked again (the connector keeps a listing once).
- **Against this goal's ceilings:** 111 of 300 requests (6 robots files, 6 terms pages, 99 to the publishers), about 7 MB of 1 GB. The connector's own record: 484 of 1,500 requests across every session.

## The tables (written under the data lock, validated, coverage, archived)

- **`large_load_waits`: 2,622 rows before, 2,745 after.** Requests followed: NYISO 74 of 81, Grant County PUD 1 of 1, Bonneville 455 of 463, Alberta (Canada) 219 of 255.
- **`large_load_wait_summary` (new, internal):** 138 rows, 26 publisher and interval cells; for each, the requests, measured, lower and upper bounds, and where five or more are measured the range of the median wait (months of 30.4375 days, the days in `x_days`; the unit vocabulary has no day). No request named, no megawatt. Each row carries its publisher's verdict and the words it rests on: NYISO internal (no license conferred), Alberta internal (non-commercial use only), **Bonneville and Grant County PUD internal by default (unclear: for Samuel's ruling)**.
- **`utility_large_load_queue_totals` (new):** 34 dated totals as printed (24 dated by the figure's own words), 9 held for their sources' terms and named in the header; from the research file of 13 November, no request made. None of the 43 rows with a figure points to a publisher that prints a dated list of requests with its own identifiers, so none could be followed by the waits' rule.
- **Registered:** the coverage tier and sector rules; `licenses.py tables`, `write` and `status` (the totals unsettled, the summary needing permission, as their publishers' verdicts say); the release list (`docs/redivis/release-v1.md`: 55 tables held out); the package catalogue; **the Redivis draft** of the totals (34 rows, and the header table's 8 lines; nothing released). The registration tests (275, 378, 410, 505, 1008 and the menu tests) pass.
- `docs/state/data_ready_c301.md` rows 13 and 14: the "Time to connect" column can take the summary once a publisher's rows are public; a hover can quote a utility's printed total.

## Commits (on `wip/c301-data`)

- The connector fixes, the summary builder, the totals in the research connector, the coverage rules; the method notes (`docs/methods/large_load_waits.md`: "Brought current", "The public summary", "Dated totals"; `docs/methods/large_load_research.md`); the metadata; the registrations; test 7008 (6 tests); test 3937 scoped to its own three tables (the totals take only rows with a figure).

## Decisions made without you

- **The Archive's listings not refreshed:** refreshing them would rewrite the saved listings of eleven side addresses too; the copies since 9 October came from the publishers.
- **The summary's medians in months** with the days beside (the precedent `interconnection_durations`), rather than a new unit in the data standard.
- **A figure's date** is the first full date its own words print, else the day read (`x_date_kind` says which).

## For Samuel's ruling

- **Bonneville's and Grant County PUD's terms for derived statistics** (Bonneville: a federal agency with no terms of use; Grant County PUD: "public record" and "All Rights Reserved"). Default: the summary's rows of both stay internal.
