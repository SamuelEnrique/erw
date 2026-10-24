# Session 2313 report: the licenses' thirtieth round (IEMOP and Noga need consent; ADME left unsettled)

24 October 2026, from 06:27 UTC to 06:31 UTC, on lab-desktop (the data machine), chain 106, unattended. Model spend USD 0. Pulls: 2 requests of 20.

## Read these first

- **Two verdicts, both from reads recorded with the outcome `read` by this chain's source sessions:**
  - **IEMOP** (read 491): "Information and/or resources contained in the Website may not be adopted, modified or reproduced without the prior written consent of IEMOP." The verdict is **needs written permission**, sold or not.
  - **Noga** (read 495): its terms bar, unless authorized in writing, "(k) use the Content on any other website or computer network for any purpose without the Company's prior written consent", non-personal use and collection by robot. The verdict is **needs written permission**, sold or not.

  The ERW holds no table from either.
- **ADME (Uruguay): no verdict.** Its open data page (read 498) speaks of open access under Law 19355 and Decree 54/2017, but names no licence. Uruguay's open data catalogue holds no data set of ADME's (reads 500 and 501; robots first, a crawl delay of 10 seconds kept), so no catalogue licence covers it. ADME stays unsettled; the ERW holds no ADME table.
- **SingStat (Singapore): no verdict.** Its terms of use page has no text in its HTML (read 489). `singstat_singapore_electricity` stays internal.
- **Not asked:** the Energy Market Authority (a bot challenge, read 484), the Philippine Statistics Authority's OpenSTAT (its robots file disallows Anthropic's agents, read 493) and Israel's statistics bureau API (an error page, read 496).
- **The record:** `licenses.py tables`, `write` and `check`: 480 tables, 129 publishers with a verdict, 0 problems. `tests.test_session205`, `207` and `887` pass; test 205's bound needed no change (501 reads, 460 later reads against 462 allowed).

## Requests (2 of 20)

| n | What | Outcome |
|---|---|---|
| 1 | catalogodatos.gub.uy/robots.txt | 200: its API and histories closed, a crawl delay of 10 s |
| 2 | the catalogue's search for ADME | 200: no data set |

Reads recorded: 500 and 501.

## Decisions made without you

- **No verdict from "acceso abierto" alone:** open access is not a reuse licence.

## For Samuel's ruling

- **IEMOP's and Noga's consent,** if the Philippines and Israel are wanted.

## Files

- Changed: `warehouse/metadata/license_verdicts.csv` (two rows), the license record (reads 500 and 501). New: this report.
