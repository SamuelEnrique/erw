# ERW: project map

The Energy Research Warehouse (ERW) is the live, citable record of the US energy system: prices, flows, projects, deals and policy across power, natural gas, oil, nuclear, renewables, storage and transmission, with the global prices and events that move US markets included. AI's demand for power is the sharpest current lens on that system, not its boundary. Coverage is US first, world later.

This is the map of the ERW for someone who has read nothing else: how a dataset travels, which document to trust when two disagree, and where things go. Modeled on the `ARCHITECTURE.md` of the Item Response Warehouse (IRW, github.com/ben-domingue/irw), including its two rules at the end.

This file is deliberately thin. Where a fact is recorded somewhere else, this file links to it rather than repeating it.

## 1. How a dataset travels

```
source (ERCOT, EIA, FERC, filings, ...)
      |
      v
warehouse/connectors/<source>_<topic>.py   one script per source, self-contained
      |
      v
warehouse/output/<table>.csv               standard shape, provenance header
      |
      v
warehouse/validate/erw_validate.py         exit 0 or the table does not move
      |
      v
warehouse/archive + bucket erw-archive     warehouse/archive/archive.py (session 28): new or changed rows,
      |                                    append only, one file per table per month (section 1a)
      v
Redivis, as a DRAFT version                 warehouse/redivis/upload.py (session 10), every table; by license
      |                                    (session 28): public tables to energy_research_warehouse, the
      |                                    rest to the private energy_research_warehouse_internal
      |
      v
   released by hand on Redivis              the ERW's warehouse of record
      |
      v
live layer: Supabase Postgres              warehouse/supabase/load.py, after the validator:
      |     (a small live set only:        writes only rows that changed; public rows readable
      |      warehouse/supabase/           with the anon key (row-level security)
      |      live_set.yaml)
      |     + latest_prices                warehouse/connectors/latest_prices.py, every 15 minutes
      v
Next.js site on Vercel (site/)             pages read Supabase with the anon key only
      |
      v
/ask and warehouse/chat/                   Claude API with four read-only tools; every number in
                                           an answer must appear in a tool result
```

The chat has two front ends over one definition: `warehouse/chat/ask.py` (Python, over the `erw` package, any backend) and the site's `/api/ask` route (TypeScript, over Supabase). `ask.py` holds the one definition (the system prompt, which is `package/llms.txt` plus the rules, the tools and the limits), and `ask.py --export-spec` writes it to `site/lib/chat/spec.json` for the site, so the two cannot drift apart. Regenerate it whenever `llms.txt`, `ask.py` or `tools.py` changes.

Three things about this are easy to get wrong:

- **Nothing publishes without a human.** An upload only ever writes a Redivis draft. Releasing it is a human click after reading the diff. No scheduled job releases anything.
- **Until the version is released, the upload has not happened.** A successful upload and a matching row count describe the draft and nothing else. Session 10 ruling: Redivis, Stanford-owned and free, is the store of record for every table, updated daily as a draft. The Supabase free tier holds only a small live set (under 300 MB), loaded after the validator from the validated tables (`warehouse/supabase/load.py`), not from a released Redivis version.
- **The live layer is derived, never edited.** If Supabase and Redivis disagree, Redivis is right and Supabase is rebuilt. Nobody writes corrections into Postgres by hand.

## 1a. The working store and the citable archive (session 28)

Ben Domingue's review (`docs/feedback/ben-2026-09-28.md`, item 1) observed that the ERW is mostly a feed, rewritten daily, while the IRW's release model fits an archive. The ERW therefore keeps three stores apart, each with one job:

| Store | What it is | Rewritten? | Who cites it |
|---|---|---|---|
| **Working store**: `warehouse/output` and the Redivis draft | The current tables. The daily run merges into the rolling windows and rewrites the full-history tables; the draft is replaced table by table | Every day | Nobody. A draft is scratch space |
| **Durable archive**: `warehouse/archive` and the private Supabase storage bucket `erw-archive` | Every row every run found new or changed, and every key it found gone, one file per table per month, append only ([`warehouse/archive/README.md`](warehouse/archive/README.md)). `warehouse/archive/restore.py` rebuilds any table as of any run | Never | The ERW itself, to recover. It is the history's only guaranteed copy |
| **Citable archive**: the released Redivis versions | A version of the dataset a human released after reading the diff | Never; a version is immutable | Everyone. This is what a paper or a tool cites |

Rules that follow:

- **The daily run touches nothing that is not recoverable.** The archive step runs before the Supabase load and the Redivis upload, and the upload is skipped on a day the archive step fails. The uploader's history gates (`warehouse/redivis/README.md`) stop a rolling-window table being replaced by a shorter one.
- **Monthly release cadence.** Once a month, in its first week, a human reviews the draft against the last released version and releases it on Redivis. That version is the citable record of the month before. A table that gives a wrong answer is fixed and released as soon as the fix lands, without waiting for the month. No scheduled job releases anything (CLAUDE.md, non-negotiable 6).
- **Rebuilding.** If the draft loses a table, or a rolling window is cut short, the table is rebuilt from the archive (`restore.py TABLE --out warehouse/output/TABLE.csv`) and uploaded again.

Everything on a clock is a GitHub Action. There is no crontab on any machine. As with the IRW, a late addition may wait for the next batched release; a released table that gives a *wrong* answer is fixed and released as soon as the fix lands.

## 2. Which document wins

| Question | Authoritative source |
|---|---|
| Table shapes, column names, units, file naming | [`docs/datastandard.md`](docs/datastandard.md) |
| Whether a table meets the standard | `warehouse/validate/erw_validate.py`. The standard states the rules; the validator is the one thing that enforces them. If they disagree, fix one of them the same day |
| Where a number came from | The header comment of its output file, then the connector that wrote it |
| Stack, non-negotiables, repo layout | [`CLAUDE.md`](CLAUDE.md) |
| What kind of work to do next | [`PRIORITIES.md`](PRIORITIES.md). Advisory; a human overrules it |
| What happened in a session and why | That session's `SESSION_*_REPORT.md`. A record, not a plan |
| What the warehouse holds today | `warehouse/metadata/coverage.csv` and `docs/coverage.md`, generated on every run |
| What a table held on an earlier day | The archive: `warehouse/archive/restore.py TABLE --as-of ...` (section 1a); a released Redivis version for what was cited |
| How an AI assistant should read the warehouse | [`package/llms.txt`](package/llms.txt), which is also the chat's system briefing |
| What each platform tool can do today | [`docs/platform-tools.md`](docs/platform-tools.md) |

`docs/datastandard.md` beats `CLAUDE.md` on output format. When a rule could plausibly belong to two documents, name its owner in this table.

## 3. Where things go inside a directory

Live scripts and standing records sit at the top level of a directory. Anything kept only for the record goes into a subfolder:

| Subfolder | Holds |
|---|---|
| `archive/` | Finished one-off scripts and reports. Nothing that runs reads them |
| `logs/`, `runs/` | Output a run writes for review. `runs/` is gitignored and disposable |
| topic folders | Everything for one job together, with a README naming whatever reads it by path |

Before moving a file, search the repository for its path: scripts, skills and provenance headers cite files by path.

## Two rules

**1. A fact lives in exactly one place; everything else links to it.** The column list lives in `docs/datastandard.md`. This file does not repeat it, so the two cannot disagree.

**2. Prefer rules that cannot go stale.** A rule enforced by `erw_validate.py` is worth more than a paragraph saying the same thing. Counts, versions and dates that move are not written into prose; point at the file or command that produces them instead.
