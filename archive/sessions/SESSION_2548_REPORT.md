# Session 2548 report: Nicaragua's electricity, not taken (CNDC draws its figures by script, for the day in progress only; INE's certificate fails)

24 October 2026, about 23:00 to 23:06 UTC, on lab-desktop (the data machine), chain 125, unattended. Precheck passed (`runs/c125/pre2548.out`). Model spend USD 0. Pulls: 7 requests of 15.

## Read these first

- **The ERW holds no Nicaraguan source.**
- **The hosts:** www.cndc.org.ni's robots file allows every path (read 1023); www.inide.gob.ni has no robots file (read 1024); **www.ine.gob.ni's certificate fails verification** (read 1025): the regulator's site was not asked again, and it joins the closed hosts.
- **CNDC** (the dispatch centre, ENATREL): its home page links no statistics files ("Copyright 2026 CNDC", read 1026); its electricity sector page is a glossary (read 1027); its charts page draws its figures by script (read 1028). The generation chart's script (read 1029) asks `graficos/consultarGeneracionPorTipo`, which takes no date: the day's dispatch in MW, a day in progress, not a month or a year. No table of months or years can be read.
- **INIDE and the central bank:** searches found no current INIDE yearbook with electricity, and the central bank's republication of CNDC's monthly figures only as a 2022 PDF; neither host was asked.
- **Not taken.**

## Requests (7 of 15)

| n | What | Outcome |
|---|---|---|
| 1 to 3 | www.cndc.org.ni, www.inide.gob.ni and www.ine.gob.ni robots files | 200, 404, certificate error |
| 4 to 6 | CNDC's home, electricity sector and charts pages | 200 |
| 7 | the generation chart's script | 200 |

Reads recorded: 1023 to 1029. Three web searches looked for CNDC's, the central bank's and INIDE's tables; they reached no publisher's host.

## Decisions made without you

- **No table for Nicaragua:** a day in progress, drawn by script, is not the months or years asked for.
- **www.ine.gob.ni closed** for its certificate.

## For Samuel's ruling

- None.

## Files

- Changed: `warehouse/metadata/license_reads.csv` (reads 1023 to 1029), `docs/licenses.md`. New: this report.
- On the data machine only: `runs/c125/s2548/`.
