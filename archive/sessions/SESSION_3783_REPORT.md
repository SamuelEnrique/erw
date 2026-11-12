# Session 3783 report: the tariff registry continued: Utah read; 16 TAC 25.194, Duke Energy Progress and the tab's utilities closed

Energy Research Warehouse (ERW). Chain 212, data machine (lab-desktop), 12 November 2026 13:27 to 13:34 UTC. Opus 5.5. Model spend USD 0. Requests: 11 of 25, each a single GET through the capped probe (`runs/c212/s3783/probe.py`, redirects at most 5; `probe.csv` lists every one); every host's robots file read alone first.

## Read these first

- **Utah's S.B. 132 is held,** read from the Legislature's enrolled copy (le.utah.gov; robots allow `/~2025/bills/`; the 10-second crawl delay was kept):
  - `large_load_connection_rules`: 8 steps with their clocks:
    - the 100 MW definition;
    - the twice-yearly processing dates;
    - missing information within 15 business days;
    - the evaluation in at most 6 months;
    - the written proposal within 15 business days;
    - 90 days to agree, or the customer may go to a generation provider;
    - the contract filed within 15 business days;
    - the PSC's decision within 60 days.
  - `utility_large_load_tariffs`: a framework row for PacifiCorp (Rocky Mountain Power, EIA 14354, `PACE`), min_demand_mw 100, written as chain 211 wrote Alabama's Act.
  - Committed `b4c442edc`. The registries check clean: 26 schedules (84 rows), and 9 documents (67 steps).
  - The tables are not yet written; they need the data lock, which the daily run holds. Session 3785 writes them.
- **Three leads closed, none read:**
  - **16 TAC 25.194 (adopted).** The PUCT's site asks permission to copy text (session 2966's verdict). The Secretary of State's TAC host (texreg.sos.state.tx.us) disallows by name Googlebot, Bingbot, GPTBot, ChatGPT-User and OAI-SearchBot. No other copy is named in the research file.
  - **Duke Energy Progress's HLF sheet.** The NCUC portal's robots file (starw1.ncuc.gov) disallows `ClaudeBot`, `anthropic-ai` and `Claude-Web` by name, and duke-energy.com answered 403 to the research file.
  - **The tab's own utilities.** Austin Energy's terms allow "no authorized use ... without explicit written permission". FirstEnergy's (FirstEnergy Pennsylvania, `pjm:grid`) say "You may not use, reproduce or distribute ... for any other purpose". Both were read from their own pages after robots allowed them; neither is a commission's filed copy.

## Requests (host, path, status)

- le.utah.gov `/robots.txt` 200; `/~2025/bills/sbillenr/SB0132.pdf` 200 (80 KB, 21 pages).
- www.puc.texas.gov `/robots.txt` 200 (`Allow: /` for `*`; not read further, because of the copy permission).
- texreg.sos.state.tx.us `/robots.txt` 200 (named agents disallowed).
- starw1.ncuc.gov `/robots.txt` 200 (ClaudeBot disallowed).
- austinenergy.com `/robots.txt`, `/sitemap.xml`, `/about/company-profile/privacy-policy`: 200 each.
- www.firstenergycorp.com `/robots.txt`, `/` (redirected to `/fehome.html` on the same host), `/corporate/website-terms.html`: 200 each.

## Decisions made without you

- **A robots file that names other AI and search agents, but not Anthropic's, is honoured as a no** (texreg.sos.state.tx.us): it bars every major crawler by name and lists no `*` rule. This is reversible, and the host is named in the note.
- **Utah's enrolled copy prints no date of its own,** so its `document_date` is the day Section 22 says the bill takes effect (7 May 2025), as its header says.
- **The PSC's rule R746-318 and Rocky Mountain Power's large-load contract application of 10 February 2026 (pscdocs.utah.gov, electric/26docs/2603505) were not read.** pscdocs.utah.gov is a new host, and the cap was kept for the other leads. They are the next Utah step.
- **The two Texas co-ops under the tab's ERCOT rows** (San Bernard, Guadalupe Valley) were not tried. Their rates are not filed with a commission, so ruling 4's public basis does not cover them.

## For Samuel's ruling

- **Texas's adopted large-load rule (16 TAC 25.194).** Both public hosts of the text refuse this reader (the PUCT's copy permission; the SOS's robots file). Recommendation: ask the PUCT for permission to quote its rules, which also opens Oncor's and CenterPoint's tariffs (`texas_delivery_charges` is internal for the same reason). Default: the step waits, said so in the method note.
