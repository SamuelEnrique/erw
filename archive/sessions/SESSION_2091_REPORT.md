# Session 2091 report: the world's reactors (the IAEA's PRIS): the terms unreadable, no table

23 October 2026, from 21:27 UTC, on lab-desktop (the data machine), the eighth session of `queue/done/068-day-26-october-data-mexico-renewables-loans-credits-pipelines.md`, unattended. Model spend USD 0. Pulls: 5 requests of 15.

## Read these first

- **No table.** The chain file asks the session to stop if the IAEA's terms forbid reuse or automated reading; they could not be read at all. The IAEA's Terms of Use page (`www.iaea.org/about/terms-of-use`) answered HTTP 403 (read 234), so www.iaea.org is not asked again, and without its terms PRIS's data would be held with no verdict.
- **PRIS itself** (`pris.iaea.org`) has no robots file (HTTP 404, read 231) and is a JavaScript application: its home page (read 232) holds no data, no link and no terms, only its scripts. A third request asked for the main script at `/PRIS/`, a wrong path (the application's base is `/`), and was answered with the home page again; it is not in the license record.
- **Added to the refused hosts** for the next file: www.iaea.org.

## The pulls

1. `pris.iaea.org/robots.txt` (read 231): 404. 2. PRIS's home page (read 232). 3. `/PRIS/main.1998896eb388d394.js`: the home page again (a wrong path). 4. `www.iaea.org/robots.txt` (read 233): site paths disallowed, not `/about`. 5. The IAEA's Terms of Use (read 234): HTTP 403.

## Decisions made without you

- **Stopped before the data:** reading PRIS's application programming interface from its script would be reading data whose terms are unknown and whose publisher's site refused the reader.

## For Samuel's ruling

- Whether to ask the IAEA for PRIS's terms, or read them in a browser; `nrc_power_reactors` holds the U.S. fleet meanwhile.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (231 to 234).
- On the data machine only: `runs/c068/s2091/`, `runs/license_reads/s2091/`.
