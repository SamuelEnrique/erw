# Session 2266 report: South Africa's grid, not taken (Eskom's terms, Stats SA's bot wall, UNdata's download gone)

24 October 2026, from 03:56 UTC, on lab-desktop (the data machine), the first session of `queue/done/103-day-6-november-data-south-africa-chile-colombia-taiwan.md`, unattended. Run by chain 090's agent, which took chain 103 when chain 099 landed (the owner's instruction: run the file the queue step prints), beside chains 101 and 102 under other agents. Model spend USD 0. Pulls: 4 requests of 15.

## Read these first

- **The next file first:** `queue/next/104-day-7-november-data-portugal-italy-japan-argentina.md` (sessions 2280 to 2293) was written, committed alone and pushed to main (`7ae30e10`) before any other work. Its snapshots read 25 pages of HTTP 402 on both sides: the site's Vercel account is blocked.
- **No table this session.**
  - **Eskom's Data Portal is not asked.** Chain 101's session 2243 read its disclaimer ("The information or data published or displayed remains the sole property of Eskom and may not be exploited by the User for any purposes, including but not limited to, commercial purposes"); its verdict is needs written permission (chain 102's agent passed this on).
  - **Statistics South Africa's monthly electricity release (P4141),** the public South African source in its place: www.statssa.gov.za's robots file allows all, but the publication page answered an Incapsula bot challenge, not the page. It is not asked again.
  - **UNdata's energy statistics** (every African country's electricity, yearly): data.un.org has no robots file (its robots address answers the site's page). Its old download handler answered HTTP 404, the site having been rebuilt, and its new data address was not found within the ceiling.
- **Chain 102's agent's other notes for this chain** (what its session 2265 would have added):
  - Taipower: data.gov.tw's robots file answered HTTP 500, and no dataset address was found outside it.
  - Decisions 73 and 74 are chain 101's; chain 102 starts at 75.
  - opendata.elia.be and transparency.apg.at are closed.
  - All of these are in queue file 104's rules.

## Requests (4 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.statssa.gov.za/robots.txt | 200: allows all |
| 2 | Stats SA's P4141 page | 200, an Incapsula challenge (212 bytes) |
| 3 | data.un.org/robots.txt | 200, the site's HTML page (no robots file) |
| 4 | UNdata's energy download handler | 404 |

Reads recorded: 404 to 407.

## Decisions made without you

- **No African source taken;** each refusal is recorded. The chain file allowed another public African grid source, and neither of the two tried served.

## For Samuel's ruling

- Eskom's Data Portal (written permission), if South Africa's grid is wanted.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv`.
- On the data machine only: `runs/c103/`.
