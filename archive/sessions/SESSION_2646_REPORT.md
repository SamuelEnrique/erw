# Session 2646 report: Guinea-Bissau's electricity not taken (INE's site unavailable; its bulletins found end in 2017)

25 October 2026, about 08:43 to 08:46 UTC, on lab-desktop (the data machine), chain 132, unattended. Precheck passed (`runs/c132/pre2646.out`). Model spend USD 0. Pulls: 3 requests of 15, all by the probe.

## Read these first

- **No table.**
- **INE:** www.stat-guinebissau.com's robots file allows `/` to `*` (read 1304; read with its comments stripped). Its sitemap lists only the home page (read 1305), and the home page answered HTTP 503 (read 1306). The site is not closed: a later chain may ask again.
- Searches found only INE's "Guine-Bissau em Numeros" bulletins of 2015 and 2017, and secondary sources whose totals disagree by a factor of two. None was taken. EAGB's own host was not found.
- **No verdict.**

## Requests (3 of 15)

| n | What | Outcome |
|---|---|---|
| 1, 2 | www.stat-guinebissau.com's robots file and sitemap | 200 |
| 3 | its home page | 503 |

Reads recorded: 1304 to 1306.

## Decisions made without you

- **Guinea-Bissau not taken;** no fetch of a 2017 bulletin, as its figures would end before 2017.

## For Samuel's ruling

- None new.

## Files

- New: this report.
- Changed: the license record (reads 1304 to 1306) and `docs/licenses.md`.
- On the data machine only: `runs/c132/s2646/`, `runs/license_reads/s2646/`.
