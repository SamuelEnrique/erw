# Session 488 report: EPA CAMPD, probed; the landing of 484 to 487's code; the next chain

21 October 2026, from 17:05 UTC, on lab-desktop (the data machine), at the owner's instruction of 21 October ("EPA CAMPD (probe only if it needs an API key)"; "land them, then write the next chain of new public sources and take it"). Model spend USD 0.

## Read these first

- **CAMPD needs an API key, so it stops at the probe.**
  - `campd.epa.gov/robots.txt` disallows nothing. `api.epa.gov` has no robots file (404).
  - The Clean Air Markets bulk-file list (`api.epa.gov/easey/camd-services/bulk-files`) answers HTTP 403 "API_KEY_MISSING: An API Key is required but was not provided. Get one at https://www.epa.gov/airmarkets/cam-api-portal."
  - The ERW holds no EPA or api.data.gov key (`.env` holds EIA's, PJM's, Anthropic's and Resend's), and getting one is a person's sign-up. Nothing more was asked.
- **The code of sessions 484 to 487 landed** on `task/484-488-connectors`, merged as `ffc3b0c0` (checks passed, run 39641658221). It holds the four connectors, their tests and sector rules, and PUDL's license record.
  - The whole suite first: one failure, `test_session205` (the read of record 85 not yet in `docs/licenses.md`), fixed by writing the document again.
  - Rule 8: `s488-land-before` and `s488-land-after`, 0 differences on 25 pages. Vercel is still rate limited, so no deployment yet; expected.
- **The four tables are not written into `warehouse/output` yet.** This machine's daily run took the data lock at 17:00:02 UTC (to 19:00 UTC, renewed while it runs). Each was built and validated in a scratch folder. Their writes, coverage, archive and license rows are the next chain's first session (489), whenever the lock is free, under its rule that no session waits for the lock.
- **The main checkout**: my copies of the four connectors there (from the trials) were checked equal to main's, or my older draft, and removed, so the daily run's own pull of main is not refused for untracked files.
- **The next chain: `queue/next/022-evening-21-october-sources.md`**, sessions 489 to 496:
  - 489: the four tables written;
  - 490: EIA's Annual Energy Outlook;
  - 491: EIA's Short-Term Energy Outlook;
  - 492: EPA's Greenhouse Gas Reporting Program, power plants;
  - 493: BOEM's offshore wind leases;
  - 494: FERC 714 before 2023;
  - 495: EIA-861 before 2025;
  - 496: the note and the next file.

  Each source gets its robots file and terms first, the connector skill's form and a cross-check. Pushed to main on its own with snapshots, then taken.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| campd.epa.gov | 1 | robots file |
| api.epa.gov | 2 | robots file (404), the bulk-file list (403, a key required) |

## For Samuel's ruling

- An EPA API key (api.data.gov, free, a sign-up) for CAMPD's hourly emissions and operations, if you want them; it would go in `.env` as `EPA_API_KEY` and through `ip.load_key`.

## Files

- New: this report, `queue/next/022-evening-21-october-sources.md` (on main).
