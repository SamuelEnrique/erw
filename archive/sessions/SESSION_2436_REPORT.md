# Session 2436 report: Armenia's electricity, not taken (the statistics committee's hosts closed); Kyrgyzstan in its place, not taken either (five years under a non-commercial licence)

24 October 2026, from 11:28 UTC to 11:33 UTC, on lab-desktop (the data machine), chain 117, unattended. Precheck passed (`runs/c117/pre2436.out`). Model spend USD 0. Pulls: 6 requests of 15.

## Read these first

- **The ERW holds no Armenian source** (`sources.csv` and the connectors on main searched for Armstat, PSRC and Armenia).
- **Armenia is not taken:**
  - armstatbank.am, the statistics committee's database, fails certificate verification at its robots file (read 792);
  - armstat.am and www.armstat.am answer HTTP 500 at theirs (reads 793 and 794), as data.gov.tw did when an earlier chain closed it;
  - the regulator PSRC (www.psrc.am) has no robots file (read 795), but a search of its site found no generation tables, only its market rules. Armenia's monthly figures appear in the press as the statistics committee's.
- **In its place, under the chain's rule, Kyrgyzstan's National Statistical Committee** (no chain has planned Kyrgyzstan):
  - www.stat.gov.kg has no robots file (read 796);
  - its open data category for electricity, gas and water (read 797) gives electricity output in million kWh for 2015 to 2019 only (13,016.6 to 15,051.2).
  - Its licence: "Open data created by the National Statistics Committee of the Kyrgyz Republic is published under the terms of the Creative Commons Attribution-NonCommercial-ShareAlike license ... 4.0 Worldwide."
  - **Not taken:** five annual figures, which Ember's table already covers, under a non-commercial licence. The licences' round (session 2439) can record the verdict from read 797.

## Requests (6 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | armstatbank.am/robots.txt | certificate fails verification |
| 2 | armstat.am/robots.txt | 500 |
| 3 | www.armstat.am/robots.txt | 500 |
| 4 | www.psrc.am/robots.txt | 404 |
| 5 | www.stat.gov.kg/robots.txt | 404 |
| 6 | stat.gov.kg's open data category 3557 | 200: five years, CC BY-NC-SA 4.0 |

Reads recorded: 792 to 797 (on this branch). Two web searches looked for the PSRC's and Armenia's system operator's figures; they reached no publisher's host.

## Decisions made without you

- **HTTP 500 at a robots file read as closed,** as chain 108 read data.gov.tw's.
- **Kyrgyzstan's five years not taken** for their brevity and their non-commercial licence.

## For Samuel's ruling

- None.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (reads 792 to 797).
- On the data machine only: `runs/c117/s2436/`.
