# Session 2739 report: the Northern Mariana Islands' electricity not taken (CUC publishes reports, not data); a redirect followed before its host's robots file

25 October 2026, about 20:50 to 20:52 UTC, on lab-desktop (the data machine), chain 138, unattended. Precheck passed (`runs/c138/pre2739.out`). Model spend USD 0. Pulls: 3 requests of 15, all by the probe.

## Read these first

- **A lapse of mine, the rule against it written after session 2656: a redirect was followed before the new host's robots file was read.**
  - The home page request to www.cucgov.org (read 1476) was redirected to cucgov.org, a host whose robots file had not been read.
  - I read cucgov.org's robots file at once afterwards (read 1477), and it allows every path to every reader, as www.cucgov.org's does (read 1475). So nothing barred was asked.
  - The order was still wrong: a home page on another host name must have its robots file read first. The probe follows redirects, so a host's bare name and its www name must both have their robots files read before any page.
- **The ERW held the Northern Mariana Islands in no table;** no source or read named CUC.
- **CUC** (cucgov.org): its home page links citizen-centric reports (fiscal 2024 and 2025), financial audits and regulations, all PDFs, with no data file (read 1476).
- **No table.** With this, none of the chain's four planned territories gave a table:
  - Puerto Rico: PDF reports;
  - the US Virgin Islands: only the latest month posted;
  - American Samoa: no figures;
  - the Northern Mariana Islands: reports only.

  The session's own choices follow in sessions 2742, 2743 and 2748.

## Requests (3 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.cucgov.org's robots file (its own request) | 200 |
| 2 | the home page (redirected to cucgov.org) | 200 |
| 3 | cucgov.org's robots file (after the redirect) | 200 |

Reads recorded: 1475 to 1477.

## Decisions made without you

- **CUC's reports not read:** a PDF's figures would not make a series within the ceiling.

## For Samuel's ruling

- None new.

## Files

- New: this report. Changed: the license record (reads 1475 to 1477) and `docs/licenses.md`.
- On the data machine only: `runs/c138/s2739/`, `runs/license_reads/s2739/`.
