# Session 3784 report: the connection rules continued: FERC behind a bot check, SPP's license unanswered

Energy Research Warehouse (ERW). Chain 212, data machine (lab-desktop), 12 November 2026 13:33 to 13:36 UTC. Opus 5.5. Model spend USD 0. Requests: 3 of 25 through the capped probe (`runs/c212/s3784/probe.csv`).

## Read these first

- **Nothing new is written.** `large_load_connection_rules` gains only session 3783's Utah steps: 9 documents, 67 steps.
- **FERC's six orders to show cause of 18 June 2026** (EL26-67 to EL26-72) remain unread.
  - www.ferc.gov's robots file allows the site, but it answers this reader with a Cloudflare challenge ("Just a moment... Enable JavaScript and cookies to continue", HTTP 403 on `/sitemap.xml`).
  - `/search/` is disallowed, and the orders' eLibrary addresses are not in the research file.
  - So the orders are still known only from the CAISO's straw proposal (held, which quotes FERC's suggested 50 MW definition) and from law-firm summaries.
- **SPP's CHILLS** (conditional service from 1 July 2026, secondhand in the research file) was not read.
  - spp.org has no robots file (404).
  - SPP's license verdict is "may be public / needs written permission" for commercial publication, and session 308 holds SPP's tables until it is answered. So this chain does not read SPP's own documents; chain 155 read SPP's HILL through FERC's order for the same reason.
- **The interruptible riders beyond the research file:** none read. The utilities under the tab's rows are closed to this reader, as recorded by sessions 2887 to 2938 and 3783.

## Requests

- www.ferc.gov `/robots.txt` 200; `/sitemap.xml` 403 (Cloudflare challenge, not passed and not retried).
- www.spp.org `/robots.txt` 404.

## Decisions made without you

- **No second request to a host that answered with a challenge.** The bot check is a refusal of this reader.
- **SPP's own pages are not read while its license is unanswered,** consistent with session 308's hold on `spp_as_prices`.

## For Samuel's ruling

- None new. SPP's license question stands (session 308): answering it opens SPP's CHILLS and its other documents.
