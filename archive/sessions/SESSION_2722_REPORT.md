# Session 2722 report: Prince Edward Island's electricity not taken (the province's site serves a bot challenge; its feed is a snapshot); queue file 138 written first

25 October 2026, about 19:14 to 19:19 UTC, on lab-desktop (the data machine), chain 137, unattended. Precheck passed first (`runs/c137/pre2722.out`). Model spend USD 0. Pulls: 2 requests of 15, both by the probe; one web search.

## Read these first

- **Queue file 138 first:**
  - `queue/next/138-day-8-december-data-puerto-rico-virgin-islands-samoa-marianas.md` (sessions 2736 to 2749) was written from file 137 by `runs/c137/write_138.py`, made by exact replacements from chain 136's writer (`runs/c137/make_write_138.py`). It keeps the rules word for word.
  - 138 was the next free number, and 2736 to 2749 were free on main and on every branch.
  - **Its sources are the US territories' grids:** Puerto Rico, the US Virgin Islands, American Samoa and the Northern Mariana Islands. The ERW is US first, and none is a source in the record or the queue (American Samoa appears only inside US tables). Guam's power authority was closed by chain 130.
  - I first wrote that "session 2587" had found American Samoa only in US tables; it was chain 127's queue file. I corrected it before the commit.
  - Pushed to main alone as `40f77d92`; snapshots `c137-q138-before` and `c137-q138-after`.
- **Chain 137's worktree:** `erw-c137` on `wip/2722-2735-data`, from main at `88eb54ef`.
- **Prince Edward Island not taken:**
  - www.princeedwardisland.ca's robots file holds Drupal's standard rules and names no Claude agent (read 1450).
  - A search found the province's electricity feed described only by third parties: a JSON of current values (on-island load, wind, oil-fired generation, exports), not a history. A private archive and a newsletter keep its past values; neither is the publisher.
  - **The province's page PEI Wind Energy served a Radware bot challenge** in place of its content (read 1451). The host is not asked again, as chain 127 closed bcn.gob.ni for the same thing.
- **No table.** Statistics Canada's tables already hold the province's monthly generation.
- **Test 205's bound** is raised by 40 for this chain's reads, from 1450.

## Requests (2 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.princeedwardisland.ca's robots file (its own request) | 200 |
| 2 | the page PEI Wind Energy | 200, a Radware challenge |

Reads recorded: 1450 and 1451.

## Decisions made without you

- **The province's host closed for its bot challenge.** No feed address from a third party's blog was tried.
- **No third party's archive taken:** the ERW takes the publisher's own figures.

## For Samuel's ruling

- None new.

## Files

- New: this report. Changed: test 205's bound, the license record (reads 1450 and 1451) and `docs/licenses.md`.
- On the data machine only: `runs/c137/s2722/`, `runs/c137/make_write_138.py`, `runs/c137/write_138.py`, `runs/c137/raise205.py`, `runs/license_reads/s2722/`.
