# ERW: project map

The map of the Energy Research Warehouse (ERW) for someone who has read nothing else: how a dataset travels, which document to trust when two disagree, and where things go. Modeled on the `ARCHITECTURE.md` of the Item Response Warehouse (IRW, github.com/ben-domingue/irw), including its two rules at the end.

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
Redivis, as a DRAFT version                 written by an uploader (not built yet)
      |
      v
   released by hand on Redivis              the ERW's warehouse of record
      |
      v
live layer: Supabase Postgres  --> Next.js site on Vercel, platform tools, Claude API
```

Three things about this are easy to get wrong:

- **Nothing publishes without a human.** An upload only ever writes a Redivis draft. Releasing it is a human click after reading the diff. No scheduled job releases anything.
- **Until the version is released, the upload has not happened.** The live layer loads from released Redivis versions only, so a successful upload and a matching row count describe the draft and nothing else.
- **The live layer is derived, never edited.** If Supabase and Redivis disagree, Redivis is right and Supabase is rebuilt. Nobody writes corrections into Postgres by hand.

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
