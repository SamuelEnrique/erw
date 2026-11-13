# Session 4102 report: the unread publishers behind the public tables (PUDL, PUCT, two outlets)

Energy Research Warehouse (ERW). Chain 229, session 3 of 50, lab-desktop third window, 13 November 2026 09:46 to 10:30 UTC. Opus 5.5. Model spend USD 0. Branch `wip/4100-licenses`.

## Read (robots first, each in its own command)

- **7 robots files** (reads 1681 to 1687):
  - **electrek.co names ClaudeBot with `Disallow: /`**, so no Electrek page was asked;
  - **www.energy-storage.news answers 403** even to its robots file, so nothing more was asked;
  - www.puc.texas.gov, www.texas.gov, www.ferc.gov and raw.githubusercontent.com (no file) allow the paths;
  - catalog.data.gov asks a 10-second crawl delay (one request was made).
- **5 pages** (reads 1688 to 1692):
  - PUDL's README: read;
  - the PUCT's link policy: read;
  - Texas.gov's site policies: 404;
  - the National Inventory of Dams on catalog.data.gov: 404;
  - FERC's open data catalog: 403 (FERC's site refuses the ERW's reader, as read 58 found in October).

## Verdicts (4 new; 263 publishers with a verdict)

- **Catalyst Cooperative (PUDL), from FERC Form 714: may be public**, sold or not. "The PUDL data and documentation are published under the Creative Commons Attribution License v4.0 (CC-BY-4.0)." (read 1688, https://raw.githubusercontent.com/catalyst-cooperative/pudl/main/README.rst, 13 November 2026)
- **Public Utility Commission of Texas: needs written permission.** "Although the content of PUCT web sites is available to the public, [...] all PUCT content is protected by federal copyright laws. [...] Site owners should contact the PUCT to request permission to use or copy content from the PUCT's website." (read 1689, https://www.puc.texas.gov/agency/about/policies/linkpolicy/, 13 November 2026)
- **Electrek and Energy-Storage.news: needs written permission, no sentence** ("NOT READ"). Their pages could not be asked. They are held at the verdict of every news outlet read in this sweep.

## What moved

- **Three tables tightened to "license needed"** under the owner's standing ruling of 12 October (flag stays public, figures held): `policy_actions`, `policy_action_tags` and `policy_reads`. They hold the PUCT's news releases. `licenses.py status`: 48 tables (was 45).
  - The state file says `/policy` loses those two tables, and `/companies` goes fully dark. Every page is in review, so no visitor sees the change.
- **Release v1:** the three are held out (136 tables in v1, 48 held out). `release_v1.py --check` reports 0 differences.
- **Two public tables settled:** `ferc714_forecast_growth` and `ferc714_planning_area_forecasts` were flagged public by the owner's ruling of 6 November and were "unsettled" (PUDL unread). They are now public by PUDL's sentence. The ERW count is 478 public, 115 internal, 55 unsettled (was 476, 115, 57).
- **21 tables wait for a ruling** (`ferc714_area_demand_2006` to `_2025`, `ferc714_respondents`): flagged internal, and PUDL's sentence allows them. **Not loosened.** `licenses.py` now labels such a table "waits for a ruling" (default "stays internal"), so "disagree" counts only open faults.
- **Disagreements:** 0 open. Not settled: 43 (was 71).

## Files kept in step

- `licenses.py write`, `status`, `check` (0 problems);
- `build_llms.py` (478 public, 170 held);
- `build_tables.py` (0 differences);
- `release_v1.py --calls-only`;
- `ask.py --export-spec` (`check_spec.py` current);
- the held count 48 in `docs/guide.md`, `package/README.md`, `package/llms.txt`;
- tests 207 (45 to 48) and 378 (the line for flags stricter than the verdict) updated.
- `license_confirm.py`: `--pick none` for a verdict with no page; passages that are not next to each other are joined with "[...]"; reStructuredText links and bullets in plain-text files.

## Tests

- **License files:** the 34 test files plus the 62 that read the package record, llms.txt, the guide or the site's verdict files: 970 passed, 30 skipped, 3 failed (275 twice, 1011). All three fixed: the release package and the chat spec.
- **Release and chat:** then 350 files that read the release package or the chat spec: 1,356 passed, 13 skipped, 0 failed.

## Decisions made without you

- **Three policy tables held** ("license needed") rather than flagged internal. They declare `License: public` in their headers, so `sources.csv` cannot set their flag, and the owner's ruling of 12 October is the rule for a public table whose publisher asks permission.
- **Their start day is 2026-10-21**, the tool's one public day (tests 215 and 248 pin it). Each row's note says chain 229 and read 1689.
- **No re-read of the four state commissions** (AZ, IL, OR, PA): their October reads found no terms at the same addresses. This waits for a better page.
- **Copied dash:** a news outlet's name with an en dash ("IEA – International Energy Agency", written to `sources.csv` by the daily run) now appears in the regenerated `site/data/table_citations.json` and the release `tables.csv`, as it would in any regeneration. The data was left alone, and a request for window A is in `docs/state/data_requests_licenses.md`.
- **Stanford package left as it is:** `release_v1.py --target stanford --check` differs by 286 rows on main and 288 here (the two FERC 714 tables). Not a gate, not regenerated.

## For Samuel's ruling

- **The policy monitor and the PUCT.** `policy_actions`, `policy_action_tags` and `policy_reads` are held because they carry the PUCT's news releases. **Default: held**, until either the PUCT's rows leave those tables (window A's connector) or the PUCT grants permission (its link policy says: contact the PUCT).
- **The 21 FERC 714 demand tables:** PUDL's CC BY 4.0 allows them, and FERC's own page still answers 403. **Default: stay internal.**
