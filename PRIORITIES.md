# What to work on

What kind of work the Energy Research Warehouse (ERW) does first. Adapted from the IRW's `PRIORITIES.md` (Item Response Warehouse, github.com/ben-domingue/irw), which ranks *kinds* of work rather than listing tasks, so the ranking stays right after every task in it is done.

Advisory: a human overrules it, and a direct request always wins. It exists so a session can place a new piece of work without asking.

Session 28 rewrote it as two layers, after Ben Domingue's review (`docs/feedback/ben-2026-09-28.md`, item 7) noted that the "Not now" list said one thing while the work did another. The warehouse keeps its list unchanged. The scores, briefs and tools that were being built on it are now named as a second layer, with its own rules, and a health gate decides when that layer may grow.

## The health gate

**No new source and no new tool while the latest daily run has failures outside the known-gap list.**

- The latest daily run is the last scheduled run on GitHub.
- The known-gap list is `warehouse/metadata/known_gaps.csv`, which a human edits and `STATUS.md` shows under "Health gate".
- `python warehouse/metadata/build_status.py --gate` exits 1 while the gate is closed.

While it is closed, a session fixes the failures (layer 1, order 1 or 2), or asks a human to accept one as a known gap. It does not start a connector or a platform tool. Fixes, gates, documentation and work a human asks for directly are not blocked.

What counts, as the daily run stands after sessions 29 to 33 (session 34):

- **A run that fails before its commit** (2026-09-29: coverage stopped it) commits no row of `run_status.csv`, so the gate would read the last run that did. The session that finds it records that run's results from the job log (runner `github`), so the gate reads the newest run.
- **A carried-forward table is not a failure.** On the runner `price_board_carbon` carries its CARB rows forward (session 30); CARB's own failure is the known gap, and coverage takes its license from the previous coverage (session 33).
- **The storage and emissions steps** (sessions 31 and 32: EIA-930 storage, its daily cycle, the CO2 workbooks and carbon intensity) count like any connector. A day EIA leaves incomplete is a `gap` row, not a failure.
- **The package test step** (session 29, required; 20 minutes at most since session 33) runs after the commit. A failed test fails the job and opens the failure issue, but it is not a table in `run_status.csv`; the next session reads the job's result and fixes it before anything else.

## Layer 1: the warehouse

The tables of what sources published, their provenance, the validator, and the stores: the working store, the archive and the released versions (`ARCHITECTURE.md` section 1a).

### The order

**1. Corpus trust: the warehouse is serving something wrong.**

Outranks everything. The question is not "is this broken" but "is a user or a platform tool getting a wrong answer right now". A missing table makes the ERW *incomplete*. A price in the wrong unit, a timestamp shifted by the daylight saving hour, a hub mislabeled, or a number with no traceable source makes it *wrong*, and wrong is worse than incomplete at any size. Every tool reads this layer; one wrong series propagates into all of them. A late addition may wait for the next release; a correction may not.

**2. Gates: stop the class, not the instance.**

Work that prevents a defect recurring beats fixing one occurrence of it. Examples of gate work:

- adding a check to `erw_validate.py`;
- making a connector fail loudly instead of writing a partial file;
- recording provenance per row;
- refusing to shrink a table's history (session 28).

The test: if you fix the instance and nothing changes about how the next one is caught, it was category 1 work, not category 2.

**3. Reach: the data gets to the people and tools that need it.**

The path from a validated CSV to the archive, then Redivis (as a draft, released by a human, monthly), then Supabase and the Next.js site, then the platform tools and the Claude API. A good table nobody can query is worth little. Reach includes documentation that lets an outside user find and cite a table.

**4. Volume: more sources, more history, more markets.**

New connectors (other ISOs, EIA, FERC, interconnection queues, datacenter and PPA events) and longer histories. This is where effort naturally goes, so ranking it fourth is not to stop it but to stop it crowding out 1 to 3 by default. A new source that arrives without provenance and without passing the validator has not arrived. A new source waits for an open health gate.

### Not now

Say so rather than quietly deferring:

- Forecasts, derived indicators and scores inside the warehouse. The warehouse holds what sources published; scoring lives in the tools on top of it.
- Paid or licensed feeds whose terms forbid redistribution.
- A custom UI for the warehouse itself beyond what Redivis and the site already give.
- Any acquisition sprint that adds sources faster than they can be validated.

## Layer 2: the platform on top

The scores, briefs and tools that read the warehouse (`docs/platform-tools.md`):

- news and policy scoring;
- the Energy Digest and the Sunday Roundup;
- the deal, datacenter, company and policy extractions;
- the Thesis Builder, Automated Analysis and `/ask`;
- the site's pages.

This is where the "Not now" items of layer 1 live: a score is a tool's output, not a source's record.

Rules for this layer:

- **It never feeds back into layer 1 unmarked.** A platform output stored as a table (a score, an extraction, a company found on the web) carries the tier `model_extracted` or `derived` (`docs/datastandard.md`, "Provenance tiers"). Every citation says so. It is cited with the source it links, never as the publisher's figure.
- **It grows only through an open health gate.** A new tool, or a new kind of score, waits until the latest daily run has no failures outside the known-gap list. Everything built on top inherits whatever is wrong underneath.
- **It is measured before it is trusted.** A model-written field ships with a spot check against its sources, recorded in the session report, before a page presents it.
- **Its order** is the same as layer 1's, within the layer:
  - wrong output first;
  - then gates (number checks, span checks, refusals);
  - then reach;
  - then new tools.

## What the ranking assumes

If any of these change, re-rank:

| | |
|---|---|
| Role | The ERW is the live, citable record of the US energy system (prices, flows, projects, deals and policy across power, natural gas, oil, nuclear, renewables, storage and transmission, plus the global prices and events that move US markets), and the shared data layer of the energy intelligence platform in `docs/platform-tools.md`. AI's demand for power is the sharpest current lens on that system, not its boundary. US first, world later |
| Labour | Claude Code agents with human review. Nothing publishes to Redivis without a human |
| Lenses | Trust first, then reach, then coverage |

## Where the detail lives

This file ranks; it does not enumerate.

- **Which document wins when two disagree:** `ARCHITECTURE.md` section 2.
- **Table format and tiers:** `docs/datastandard.md`.
- **The gate's inputs:** `STATUS.md` and `warehouse/metadata/known_gaps.csv`.
- **What was done and what is open:** the latest `archive/sessions/SESSION_*_REPORT.md`.
