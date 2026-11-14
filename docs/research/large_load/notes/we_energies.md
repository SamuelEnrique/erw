# Wisconsin Electric Power Company (We Energies) (WI): large-load rules

Energy Research Warehouse (ERW), research pass of session 5300 (portable laptop, window P4). Method: `../README.md`.

<!-- generated: start -->

Group `great_lakes`. Rows in `utilities_<date>.csv`:

- **great_lakes-06**: Rate Schedule VLC, Very Large Customer - Market Pricing Tariff, with Rate Schedule BRT, Bespoke Resources Tariff (Sheets 238 to 266 and following). Status: in effect (2026-06-01). License: internal. Source: https://www.we-energies.com/pdfs/etariffs/wisconsin/elecrateswi.pdf
  - Not published in the documents read: study_timeline.
  - Notes: The PSCW's ERF and docket pages (apps.psc.wi.gov) refuse Claude's agents by robots, so the PSCW order of 21 May 2026 in 6630-TE-113 was not read. Charges (2025 dollars): Fixed Administrative Charge 213,118 USD per billing period per customer; Demand-Based Administrative Charge 305 USD per MW of Customer Maximum Demand (Sheet 245); energy at MISO pass-through, no fuel adjustment. Non-firm load above the Firm Service Level is curtailable at MISO EEA2; failure to curtail is charged at MISO Value of Lost Load (Sheets 243 and 244). Bespoke resources carry a fixed return on equity of 10.48% to 10.98% on a 57% equity ratio (Sheet 250). Oracle (Port Washington) has met its financial security obligations per the WEC deck (slide 13).

Refused or blocked (not read, not retried another way):

- https://apps.psc.wi.gov/APPS/dockets/content/detail.aspx?id=6630&case=TE&num=113: robots.txt 200: DISALLOWED for ClaudeBot, Claude-Web, anthropic-ai (the PSCW docket and ERF host)

<!-- generated: end -->
