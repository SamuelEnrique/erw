# Session 924 report: Ember's yearly electricity data not taken (its file host's robots file disallows it)

23 October 2026, from 09:49 UTC, on lab-desktop (the data machine), a session of `queue/done/052-day-23-october-data-world-oil-reactors-stocks.md`. Model spend USD 0. Pulls: 4 requests of 15 (ember-energy.org's robots file, asked alone first; the Yearly Electricity Data page; files.ember-energy.org's robots file; and, wrongly, the data file on that host).

## Read these first

- **Not taken.** Ember's page (`https://ember-energy.org/data/yearly-electricity-data/`, allowed by ember-energy.org's robots file) links its data as CSV files on another host, `files.ember-energy.org`, whose robots file reads `User-agent: *`, `Disallow: /`, `Allow: /*.pdf$`: every path but PDFs is closed to automated readers.
- **An error of this session:** the robots request and the CSV fetch ran in one command, so the file (`release_generation_yearly_global.csv`, 16 MB, 104,241 rows, last modified 19 October 2026) was fetched before the robots answer was read. It was moved out of `warehouse/raw/` (to `runs/c052/s924/robots_disallowed/`, on this machine only) and is not used; no table, test or connector was written from it.
- **The license would have allowed it:** "All content is released under a Creative Commons Attribution Licence (CC-BY-4.0)", on every Ember page. The block is the robots file, not the terms.
- **The cross-check the queue file asked (Ember against session 909's EIA table) was not run.**

## Decisions made without you

- **The fetched file set aside, not used,** since the ERW reads only what a publisher's robots file allows.

## For Samuel's ruling

- **Ember's data:** whether to ask Ember for automated access to `files.ember-energy.org` (or a key to its API), or to leave Ember to a person's download. Its license (CC BY 4.0) allows the data; its file host's robots file does not allow a reader.

## Errors

- The fetch above, made in the same command as the robots request. From this session on, a new host's robots file is asked in a call of its own and read before any other request to that host is written.

## Files

- New: this report.
- On the data machine only: `runs/c052/s924/` (the probe record and the set-aside file), `runs/license_reads/s924/`.
