# Session 2710 report: Saskatchewan's electricity not taken (SaskPower's terms require written permission to download)

25 October 2026, about 17:02 to 17:06 UTC, on lab-desktop (the data machine), chain 136, unattended, while this machine's own daily task held the data lock. Precheck passed (`runs/c136/pre2710.out`). Model spend USD 0. Pulls: 5 requests of 15, all by the probe; one web search, which found nothing from SaskPower.

## Read these first

- **The ERW held Saskatchewan only in Statistics Canada's tables;** no source or read named SaskPower.
- **SaskPower** (www.saskpower.com):
  - It has no robots file (HTTP 404, read 1437), so it states no rule.
  - Its page Where Your Power Comes From draws a daily snapshot by script: demand, generation and imports averaged over 24 hours, with no history (read 1440). Its annual figures are in its current reports.
  - **Its Digital Terms and Conditions** (February 2022, a PDF linked from its terms page, read 1441), section 10, Limited License: the site is "for your informational, non-commercial and personal use only", and "You shall not market, commercially exploit, reproduce, copy, download, derivatize, modify or distribute any content, this Website or any services, in whole or in part, without SaskPower's written permission." Section 8 names data among the content. No report was fetched, and the host is not asked again.
- **No table.** No replacement was tried: Statistics Canada's tables already hold Saskatchewan's generation and trade.

## Requests (5 of 15)

| n | What | Outcome |
|---|---|---|
| 1 | www.saskpower.com's robots file (its own request) | 404 |
| 2 | the home page | 200 |
| 3 | the Terms and Conditions page | 200 |
| 4 | Where Your Power Comes From | 200 |
| 5 | the Digital Terms and Conditions (PDF) | 200 |

Reads recorded: 1437 to 1441.

## Decisions made without you

- **SaskPower closed for its terms,** which require written permission to download. Its verdict (written permission) goes to session 2713's round.

## For Samuel's ruling

- **SaskPower's permission** would open its annual generation by source and interchange.

## Files

- New: this report. Changed: the license record (reads 1437 to 1441) and `docs/licenses.md`.
- On the data machine only: `runs/c136/s2710/`, `runs/license_reads/s2710/`.
