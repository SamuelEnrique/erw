# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in this repository.

It is adapted from the `CLAUDE.md` of the Item Response Warehouse (IRW, github.com/ben-domingue/irw), whose owner has allowed us to copy its infrastructure and documents. Where this file and the IRW differ, this file governs the ERW.

## What the ERW is

The **Energy Research Warehouse (ERW)** is the live, citable record of the US energy system: prices, flows, projects, deals and policy across power, natural gas, oil, nuclear, renewables, storage and transmission, with the global prices and events that move US markets included. AI's demand for power is the sharpest current lens on that system, not its boundary. Coverage is US first, world later. Every source is reshaped into a small number of standard table shapes so that they can be joined and compared. The ERW is the shared data layer of a 31-tool energy intelligence platform (20 until session 18, 25 since session 19, 26 since session 23, 31 in the plan since session 24, five of them planned) ([`docs/platform-tools.md`](docs/platform-tools.md)). Every tool on that platform reads the ERW; none keeps its own private copy of a source.

Note on the name: in sustainability circles "ERW" also means enhanced rock weathering. In this repository ERW always means Energy Research Warehouse.

**Start with [`ARCHITECTURE.md`](ARCHITECTURE.md):** how a dataset travels, and which document wins when two disagree.

## The stack

| Layer | Tool | Role |
|---|---|---|
| Ingestion | Python 3 | One connector per source in `warehouse/connectors/`, writing standard CSVs to `warehouse/output/` |
| Warehouse of record | Redivis | The published, versioned copy of every table (`warehouse/redivis/`). Uploads write a draft; what Redivis has released is what the ERW says |
| Live layer | Supabase Postgres | A small live set (`warehouse/supabase/`): public reads through row-level security. Derived from the warehouse, never the other way round |
| Public site | Next.js on Vercel (`site/`) | Price board, prices, digest, data and methods, the ERCOT peak-premium explorer, and `/ask`. Reads Supabase with the anon key only |
| Schedules | GitHub Actions | Everything that runs on a clock (`.github/workflows/`: the daily run, the 15-minute latest prices, and the Sunday Energy Roundup with Automated Analysis). No crontabs on anyone's machine |
| Scoring and chat | Claude API | News scoring, the weekday digest with its fun fact and the Sunday Roundup (`warehouse/news/`), the chart-of-the-week note (`warehouse/analysis/`), and question answering over the warehouse (`warehouse/chat/`, `/ask`) |

## Non-negotiables

1. **Real data only.** Never generate, fabricate, or fill in placeholder numbers. If a data pull fails, fail loudly, log the exact error, and continue with other work. No output file is better than a partial or synthetic one.
2. **No em dashes** in any file written to this repository. Use commas, periods, or colons.
3. **Do not delete or overwrite existing files.** Read them first and extend them.
4. **Commit after each unit of work** with a clear message. The daily workflow commits and pushes metadata; sessions push only after merging origin/main (session 28: this replaces "do not push unless a human asks", which the workflow never followed).
5. **Every number traces to its source.** Each output file records, in its header comment and in the run log, the exact source report it came from and when it was retrieved.
6. **Nothing publishes to Redivis without a human.** Uploads, when they exist, write a draft version only. Releasing a Redivis version is always a human click after reviewing the diff. No scheduled job ever publishes.
7. **Gate commands are never piped.** The validator, the coverage builder, the tests, the site build and the loader are run so that their own exit code is what the shell sees: no `| tail`, `| head`, `| grep` or `| tee` after them (a pipe returns the last command's status and hides a failure), and the exit code is read before the next step. To keep a long output, redirect it to a file and print the exit code (`cmd > runs/x.out 2>&1; echo "exit=$?"`). Session 64's `build_coverage.py | tail` hid a failed build and the loader ran on stale coverage; since session 65 the loader also refuses to run when `coverage.csv` no longer describes the tables on the machine.

## The live pages and the freeze

The pages open to visitors (`live` in `site/lib/release.ts`, the one list): `/`, `/cost-of-power/battery`, `/cost-of-power/seller`, `/network`, `/storage` and `/about` (About), with `/terms` and the four methods pages those tools link to. Every other page is `review`, and every new page starts as `review`.

8. **No deploy without a before and after snapshot of the live pages, every difference listed.** A push to `main` or to a `task/` branch deploys. Before it, `node site/scripts/snapshot-live.mjs take <before>`; after the deploy, `take <after>` and `compare <before> <after>`. The comparison's lines go into the session report, each marked expected or not; a difference that was not meant is reported at the top of the report. The same holds for a load into the live set of a table a live page reads. The script reads 20 pages as a visitor (the six above, with the battery page for both grids at 2, 4 and 8 hours under both strategies and, since session 82, the seller tab's California solar and wind) and keeps each page's HTML, every checked number and the visible text in `runs/snapshots/` (session 76 found the rule; session 77 made it permanent).
9. **A freeze is honoured by every session.** While a reviewer is using the site, no session changes what a visitor sees on a live page, or any table a live page reads, unless its prompt names the one deploy that may. Sessions push to `wip/` branches and write the exact remaining commands under "To finish". **Current freeze: 3 October 2026 to 6 October 2026** (a reviewer is using the live site until 6 October).

## Repository layout

| Path | Contents |
|---|---|
| `warehouse/connectors/` | One self-contained Python script per source. Each pulls, reshapes to the data standard, and writes to `warehouse/output/` |
| `warehouse/output/` | Standard-shaped CSVs, each with a provenance header comment. Everything here should pass the validator. Not in git (session 9) except the news tables; backed up in Redivis |
| `warehouse/validate/` | `erw_validate.py`, the one validator. It is the gate a table passes before upload |
| `warehouse/derived/` | Tables the ERW computes from other ERW tables (the ERCOT peak premium), each with a method in `docs/methods/` |
| `warehouse/news/` | News ingest, scoring (rubric in `rubric.md`) and the daily Energy Digest (`docs/digest/`) |
| `warehouse/metadata/` | `coverage.csv` (generated), `sources.csv` (the source registry and licenses), `run_status.csv` (every run and every gap) |
| `warehouse/redivis/`, `warehouse/supabase/` | The uploader to the Redivis draft, and the Supabase migrations, live set and loader |
| `warehouse/chat/` | Question answering: four tools over the `erw` package, the loop with its number check, and the evaluation set |
| `package/` | The `erw` Python client (local, Redivis and Supabase backends) and `llms.txt`, the briefing for AI assistants |
| `site/` | The public Next.js site; its README has the Vercel steps |
| `docs/datastandard.md` | The ERW data standard. Single source of truth for table shapes, column names, units and file naming |
| `docs/coverage.md`, `docs/platform-tools.md` | What the warehouse holds (generated), and the status of each of the 20 platform tools |
| `.claude/skills/` | Claude Code skills for repeatable ERW workflows |
| `PRIORITIES.md` | What kind of work to do next |
| `archive/sessions/` | Per-session prompts and reports (`SESSION_*_PROMPT.md`, `SESSION_*_REPORT.md`): what was asked, what was built, decisions, errors, open questions (moved from the root in session 28) |
| `warehouse/archive/` | The append-only durable store (session 28): every table's new or changed rows by month, copied to the private Supabase storage bucket `erw-archive`; `restore.py` rebuilds any table (`ARCHITECTURE.md` section 1a) |

## Running things

```bash
pip install -r requirements.txt
bash warehouse/run_daily.sh                               # the full daily sequence, as the workflow runs it
python warehouse/validate/erw_validate.py warehouse/output/*.csv   # a gate: never piped, read its exit code
python warehouse/supabase/load.py                         # the live set (writes only what changed)
python warehouse/chat/ask.py "question"                   # ask the warehouse
cd site && npm install && npm run build && npm start      # the public site
```

Validator exit codes: `0` pass, `1` blocked, `2` bad input.

## Data format

The full rules live in **[`docs/datastandard.md`](docs/datastandard.md)**, which overrides this file on output format. Quick reference: there are three table shapes, `series` (one row per observation: `entity, variable, ts_utc, value` first), `entities` (one row per physical or corporate thing) and `events` (one row per deal, filing or announcement). Timestamps are UTC. Power is MW, prices are USD per MWh, unless a `unit` column says otherwise.

## Key conventions

- Connectors are self-contained. Do not introduce shared dependencies between connectors until two of them need the same code.
- Connectors write CSV only, with a `#` comment header naming the source report, source URL and retrieval timestamp.
- Credentials live outside the repository and are read from the environment. Never commit a key.
- When a decision has to be made without a human, make a reasonable one, write it down in the session report, and continue.
