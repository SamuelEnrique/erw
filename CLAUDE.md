# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working in this repository.

It is adapted from the `CLAUDE.md` of the Item Response Warehouse (IRW, github.com/ben-domingue/irw), whose owner has allowed us to copy its infrastructure and documents. Where this file and the IRW differ, this file governs the ERW.

## What the ERW is

The **Energy Research Warehouse (ERW)** is an open, harmonized warehouse of energy data: prices, loads, generation, plants, projects, datacenters, deals and filings, reshaped into a small number of standard table shapes so that they can be joined and compared. It is the shared data layer of a 20-tool energy intelligence platform focused on power as the constraint on AI. Every tool on that platform reads the ERW; none keeps its own private copy of a source.

Note on the name: in sustainability circles "ERW" also means enhanced rock weathering. In this repository ERW always means Energy Research Warehouse.

**Start with [`ARCHITECTURE.md`](ARCHITECTURE.md):** how a dataset travels, and which document wins when two disagree.

## The stack

| Layer | Tool | Role |
|---|---|---|
| Ingestion | Python 3 | One connector per source in `warehouse/connectors/`, writing standard CSVs to `warehouse/output/` |
| Warehouse of record | Redivis | The published, versioned copy of every table. What Redivis has released is what the ERW says |
| Live layer | Supabase Postgres, and a Next.js site on Vercel | Fast reads for the platform tools and the public site. Derived from the warehouse, never the other way round |
| Schedules | GitHub Actions | Everything that runs on a clock. No crontabs on anyone's machine |
| Scoring and chat | Claude API | Scoring, classification and the chat surface over the warehouse |

## Non-negotiables

1. **Real data only.** Never generate, fabricate, or fill in placeholder numbers. If a data pull fails, fail loudly, log the exact error, and continue with other work. No output file is better than a partial or synthetic one.
2. **No em dashes** in any file written to this repository. Use commas, periods, or colons.
3. **Do not delete or overwrite existing files.** Read them first and extend them.
4. **Commit after each unit of work** with a clear message. Do not push unless a human asks.
5. **Every number traces to its source.** Each output file records, in its header comment and in the run log, the exact source report it came from and when it was retrieved.
6. **Nothing publishes to Redivis without a human.** Uploads, when they exist, write a draft version only. Releasing a Redivis version is always a human click after reviewing the diff. No scheduled job ever publishes.

## Repository layout

| Path | Contents |
|---|---|
| `warehouse/connectors/` | One self-contained Python script per source. Each pulls, reshapes to the data standard, and writes to `warehouse/output/` |
| `warehouse/output/` | Standard-shaped CSVs, each with a provenance header comment. Everything here should pass the validator |
| `warehouse/validate/` | `erw_validate.py`, the one validator. It is the gate a table passes before upload |
| `docs/datastandard.md` | The ERW data standard. Single source of truth for table shapes, column names, units and file naming |
| `.claude/skills/` | Claude Code skills for repeatable ERW workflows |
| `PRIORITIES.md` | What kind of work to do next |
| `SESSION_*_REPORT.md` | Per-session logs: what was built, decisions, errors, open questions |

## Running things

```bash
pip install -r requirements.txt
python warehouse/connectors/ercot_prices.py
python warehouse/validate/erw_validate.py warehouse/output/*.csv
```

Validator exit codes: `0` pass, `1` blocked, `2` bad input.

## Data format

The full rules live in **[`docs/datastandard.md`](docs/datastandard.md)**, which overrides this file on output format. Quick reference: there are three table shapes, `series` (one row per observation: `entity, variable, ts_utc, value` first), `entities` (one row per physical or corporate thing) and `events` (one row per deal, filing or announcement). Timestamps are UTC. Power is MW, prices are USD per MWh, unless a `unit` column says otherwise.

## Key conventions

- Connectors are self-contained. Do not introduce shared dependencies between connectors until two of them need the same code.
- Connectors write CSV only, with a `#` comment header naming the source report, source URL and retrieval timestamp.
- Credentials live outside the repository and are read from the environment. Never commit a key.
- When a decision has to be made without a human, make a reasonable one, write it down in the session report, and continue.
