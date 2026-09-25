# What to work on

What kind of work the Energy Research Warehouse (ERW) does first. Adapted from the IRW's `PRIORITIES.md` (Item Response Warehouse, github.com/ben-domingue/irw), which ranks *kinds* of work rather than listing tasks, so the ranking stays right after every task in it is done.

Advisory: a human overrules it, and a direct request always wins. It exists so a session can place a new piece of work without asking.

## The order

**1. Corpus trust: the warehouse is serving something wrong.**

Outranks everything. The question is not "is this broken" but "is a user or a platform tool getting a wrong answer right now". A missing table makes the ERW *incomplete*. A price in the wrong unit, a timestamp shifted by the daylight saving hour, a hub mislabeled, or a number with no traceable source makes it *wrong*, and wrong is worse than incomplete at any size. Twenty tools read this layer; one wrong series propagates into all of them. A late addition may wait for the next release; a correction may not.

**2. Gates: stop the class, not the instance.**

Work that prevents a defect recurring beats fixing one occurrence of it. Adding a check to `erw_validate.py`, making a connector fail loudly instead of writing a partial file, and recording provenance per row are gate work. The test: if you fix the instance and nothing changes about how the next one is caught, it was category 1 work, not category 2.

**3. Reach: the data gets to the people and tools that need it.**

The path from a validated CSV to Redivis (as a draft, released by a human), then to Supabase and the Next.js site, then to the platform tools and the Claude API. A good table nobody can query is worth little. Reach includes documentation that lets an outside user find and cite a table.

**4. Volume: more sources, more history, more markets.**

New connectors (other ISOs, EIA, FERC, interconnection queues, datacenter and PPA events) and longer histories. This is where effort naturally goes, so ranking it fourth is not to stop it but to stop it crowding out 1 to 3 by default. A new source that arrives without provenance and without passing the validator has not arrived.

**5. Not now.** Say so rather than quietly deferring:

- Forecasts, derived indicators and scores inside the warehouse. The warehouse holds what sources published; scoring lives in the tools on top of it.
- Paid or licensed feeds whose terms forbid redistribution.
- A custom UI for the warehouse itself beyond what Redivis and the site already give.
- Any acquisition sprint that adds sources faster than they can be validated.

## What the ranking assumes

If any of these change, re-rank:

| | |
|---|---|
| Role | The ERW is the shared data layer of a 20-tool energy intelligence platform focused on power as the constraint on AI |
| Labour | Claude Code agents with human review. Nothing publishes to Redivis without a human |
| Lenses | Trust first, then reach, then coverage |

## Where the detail lives

This file ranks; it does not enumerate. Which document wins when two disagree: `ARCHITECTURE.md` section 2. Table format: `docs/datastandard.md`. What was done and what is open: the latest `SESSION_*_REPORT.md`.
