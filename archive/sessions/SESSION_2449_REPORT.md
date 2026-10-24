# Session 2449 report: Senegal not taken (Senelec and CRSE reserve all rights, ANSD's certificate does not verify); Slovenia and Cyprus tried and closed

24 October 2026, from 12:38 UTC, on lab-desktop (the data machine), the second session of `queue/done/118-day-18-november-data-rwanda-senegal-azerbaijan-uzbekistan.md`, unattended. Precheck passed (`runs/c118/pre2449.out`). Model spend USD 0. Pulls: 9 of 15 (below).

## Read these first

- **Senegal not taken:**
  - **Senelec:** no robots file (HTTP 404, read 772). The home page's footer reads "© 2026 - Tous droits réservés par la SENELEC", and no terms of use or grant of reuse were found (read 773). New verdict: needs written permission.
  - **CRSE, the regulator:** its robots file allows the reader (read 774). Its footer reads "© Copyright 2025, CRSE. Tous droits réservés.", and its legal notice link leads nowhere (read 775). New verdict: needs written permission.
  - **ANSD, the statistics agency:** its certificate does not verify (read 776). TLS was not bypassed.
  - These follow the rule chains 114 and 115 agreed on, NamPower's and ERB Zambia's: a footer reserving all rights with no grant means needs written permission.
- **Two replacements tried and closed:**
  - **Slovenia's statistics office:** pxweb.stat.si's robots file disallows `/sistatdata/` for every reader, and every path for ClaudeBot, GPTBot and others by name (read 777). It is honoured and not asked again.
  - **TSO Cyprus:** no robots file (read 778) and no terms stated (read 779). Its generation records are load-duration curves in PDFs (read 780), and its other data pages would not fit the six requests left.
- **No table this session.** The chain's own-choice sessions follow.

## Pulls against their ceilings

| Host | Requests | What |
|---|---|---|
| www.senelec.sn | 2 | robots (404), the home page |
| www.crse.sn | 2 | robots, the home page |
| www.ansd.sn | 1 | robots (no response: certificate) |
| pxweb.stat.si | 1 | robots |
| tsoc.org.cy | 3 | robots (404), the home page, the generation records page |
| total | 9 of 15 | |

## Errors

- None.

## Decisions made without you

- **No table rather than one from publishers reserving all rights,** as for NamPower and ERB Zambia.

## For Samuel's ruling

- **Senelec's and CRSE's consent,** if Senegal's figures are wanted.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (772 to 780), `license_verdicts.csv` (Senelec, CRSE), `license_tables.csv`, `docs/licenses.md`.
- On the data machine only: `runs/c118/s2449/`, `runs/license_reads/s2449/`.
