# Session 691 report: HIFLD's successor, probed: none found

23 October 2026, from 00:26 UTC, on lab-desktop (the data machine), a session of `queue/done/045-evening-22-october-data-resumed.md`. Model spend USD 0.

## Read these first

- **No federal publisher releases substations or transmission lines today under a line the ERW can cite** ([`docs/reviews/siting-sources-2026-10-24.md`](../../docs/reviews/siting-sources-2026-10-24.md)). EIA's Energy Atlas lists no transmission layer of its own; the national lines survive as Esri's archive, **licensed under Esri's Master License Agreement** (not public, "no longer updated or maintained"), and as users' copies with no license line; a NETL (DOE) user's layer has no description or copyright text; the federal GeoPlatform organization holds one user's 2023 upload; data.gov's catalogue API answers 404.
- **So sessions 692 and 693 write nothing** (the chain: "a refusal: the session writes what it found and probes nothing else"). The names `hifld_substations` and `hifld_transmission_lines` stay reserved.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| atlas.eia.gov | 2 | robots file; the Atlas's catalogue search |
| www.arcgis.com | 2 | two catalogue searches |
| services1.arcgis.com | 2 | robots file (403); a service directory |
| services6.arcgis.com | 2 | robots file (403); NETL's service |
| catalog.data.gov | 2 | robots file; the catalogue search (404) |
| all | **10 of 12** | |

## Decisions made without you

- Two requests left unused: the leads they could have reached (the GeoPlatform, data.gov's new interface) each need a robots file and a search, more than two requests.
- The Atlas's two requests came a second apart, inside its 60-second crawl delay: noted in the review, not repeated.
- No license record changed: no terms page was reached besides EIA's record 1.

## For Samuel's ruling

- A publisher of record for substations and transmission lines, if you know one; or whether Esri's licensed archive of the lines may be used.

## Files

- New: `docs/reviews/siting-sources-2026-10-24.md`, this report. On the data machine only: `runs/c045/s691/`, `runs/license_reads/s691/`.
