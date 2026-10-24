# Session 2241 report: Australia's market demand: not taken (AEMO, energy.gov.au and the AER refuse the reader); Swissgrid in its place: not taken (its terms)

24 October 2026, from 03:32 UTC, on lab-desktop (the data machine), the fourth session of `queue/done/101-day-4-november-data-france-spain-brazil-australia.md`, unattended. Model spend USD 0. Pulls: 7 requests of 15 (below).

## Read these first

- **AEMO's data are closed to the ERW's reader.** nemweb.com.au's robots file answers HTTP 403 with a Cloudflare challenge served from www.aemo.com.au (read 419). Neither host is asked again. Passing a challenge would be evading it.
- **Two Australian Government hosts that publish the same quantities reset the connection** at their robots files: www.energy.gov.au (the Australian Energy Statistics, read 420) and www.aer.gov.au (the AER's wholesale statistics, read 421). Neither is asked again.
- **Swissgrid tried in Australia's place** under the queue file's rule (a source that cannot be taken is replaced by another public one). Its robots file allows every path (read 422), and its generation page links yearly energy overview workbooks for 2009 to 2026 (read 424). **Its legal information** (read 425) gives a new verdict, needs written permission in both columns: "Accessing the Swissgrid website, downloading, and copying data from this website or its parts do not give the user any rights to content, the software, the registered trademark or other website elements. Any modification, reproduction or use of the website, the Swissgrid logo or its parts for public or commercial purposes without the prior consent of Swissgrid is strictly prohibited." The workbooks were not fetched.
- **No table was written.** Australia's demand stays as Ember's yearly figure through Our World in Data (`owid_ember_electricity_annual`).

## The pulls

1. nemweb.com.au/robots.txt (read 419): HTTP 403, a challenge.
2. www.energy.gov.au/robots.txt (read 420): the connection reset.
3. www.aer.gov.au/robots.txt (read 421): the connection reset.
4. www.swissgrid.ch/robots.txt (read 422).
5. Swissgrid's English sitemap (read 423), for the pages' real addresses.
6. The grid data generation page (read 424).
7. The legal information (read 425).

## Errors

- None.

## Decisions made without you

- **Australia not taken** without a challenge-passing or a disguised reader.
- **Swissgrid tried, then left at its terms.** Its workbooks' addresses are in read 424, should you obtain consent.

## For Samuel's ruling

- **AEMO's data** (nemweb.com.au, Cloudflare-challenged) and **Swissgrid's energy overview** (needs prior consent) are open only with the publishers' agreement. Undone: whether to ask either.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (374 to 380), `warehouse/metadata/license_verdicts.csv` (Swissgrid), `docs/licenses.md`.
- On the data machine only: `runs/c101/s2241/`, `runs/license_reads/s2241/`.
