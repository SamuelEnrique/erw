# Session 2310 report: Israel's grid, not taken (Noga's terms forbid reuse; the statistics bureau's API refused the reader)

24 October 2026, from 06:10 UTC to 06:12 UTC, on lab-desktop (the data machine), chain 106, unattended. Model spend USD 0. Pulls: 4 requests of 15.

## Read these first

- **No table this session.**
- **Noga, the system operator:** its robots file allows the site but its CMS, install, search and test paths, and names no AI agent. Its sitemap lists statistics pages (annual consumption, annual hourly consumption, the demand curve, generation by source). But its terms of use (read 495) bar, "unless expressly authorized in writing by the Company", these uses:
  - "use the Website and/or the Content for commercial or non-personal purposes";
  - "use the Content on any other website or computer network for any purpose without the Company's prior written consent";
  - collecting information "by using any robot, spider, crawler".

  Noga goes to the licenses round (session 2313) as needs written permission. No data page was asked.
- **The Central Bureau of Statistics' API** (apis.cbs.gov.il), the public alternative: its robots address answered an error page with an incident number ("Oops, Something is wrong"), not a robots file. It is read as a refusal and was not asked again.

## Requests (4 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.noga-iso.co.il/robots.txt | 200: CMS paths only |
| 2 | Noga's sitemap | 200: 439 addresses |
| 3 | Noga's terms of use | 200: written consent for any non-personal use |
| 4 | apis.cbs.gov.il/robots.txt | 200: an error page with an incident number |

Reads recorded: 494 to 496.

## Decisions made without you

- **The statistics bureau's error page read as a refusal,** not asked again.

## For Samuel's ruling

- **Noga's consent** for Israel's demand and generation.

## Files

- New: this report. Changed: the license record (reads 494 to 496).
- On the data machine only: `runs/c106/s2310/`.
