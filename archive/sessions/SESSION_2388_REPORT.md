# Session 2388 report: Bolivia's generation, not taken (CNDC's figures load through a nonce-guarded AJAX call; all rights reserved)

24 October 2026, from 09:22 UTC to 09:24 UTC, on lab-desktop (the data machine), chain 113, unattended. Model spend USD 0. Pulls: 3 requests of 15.

## Read these first

- **No table this session.**
- **CNDC:** its robots file disallows WordPress's admin path only and names no AI agent (read 604). Its sitemap lists history pages for demand, peak load, capacity and marginal cost. But the demand history page holds no figures in its HTML ("Cargando datos…"). They come through WordPress's `admin-ajax.php` with a nonce issued to the page, a scripted request rather than a published file or open endpoint. The footer reads "Todos los derechos reservados" (read 605). No data request was made.
- Ember's annual table already covers Bolivia.

## Requests (3 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.cndc.bo/robots.txt | 200: WordPress's admin path only |
| 2 | CNDC's page sitemap | 200: 33 pages, the history pages among them |
| 3 | the demand history page | 200: figures by AJAX with a nonce; all rights reserved |

Reads recorded: 604 and 605.

## Decisions made without you

- **No nonce-guarded AJAX request** made in place of a published file or endpoint.

## For Samuel's ruling

- None new.

## Files

- New: this report. Changed: the license record (reads 604 and 605).
- On the data machine only: `runs/c113/s2388/`.
