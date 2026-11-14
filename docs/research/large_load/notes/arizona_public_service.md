# Arizona Public Service Company (AZ): large-load rules

Energy Research Warehouse (ERW), research pass of session 5300 (portable laptop, window P4). Method: `../README.md`.

<!-- generated: start -->

Group `southwest_california`. Rows in `utilities_<date>.csv`:

- **southwest_california-02**: Rate Schedule XHLF revision proposed in APS's 2025 rate case (direct assignment of generation costs to extra high load factor customers). Status: proposed (2025-06-13). License: public. Source: https://www.sec.gov/Archives/edgar/data/764622/000076462226000055/novemberinvestordeck.htm
  - Not published in the documents read: threshold_mw, min_demand, contract_term, collateral, exit_fee, study_timeline, connection_timeline.
  - Overlap with window A's registries: large_load_tariffs/aps_xhlf.yaml holds Rate Schedule XHLF in effect (A.C.C. No. 6067, Decision No. 79293, effective 2024-03-08); this row is the pending revision in E-01345A-25-0105, whose sheet was not read. No held value differs.
  - Notes: Decision expected December 2026 (investor deck; the 10-Q says the hearing concluded on 7 July 2026). Not read: the proposed XHLF redline and clean sheets and the Hobbick testimony (s22.q4cdn.com refused, robots 403; docket.images.azcc.gov refused, robots disallow; images.edocket.azcc.gov refused, certificate mismatch). APS's own pages (aps.com, terms limit use to personal noncommercial use) say the June 2025 request proposed a 45 percent increase for extra-large users and name minimum bill and collateral requirements without figures: internal leads only. The Q3 2026 10-Q (sec.gov, pnw-20260930.htm) reports a Direct Pricing Contract signed 16 October 2026 with TSMC Arizona, ramping to about 1.88 GW for an initial term of 25 years, with upfront payments for credit support and liquid and non-liquid collateral from 1 January 2027, to be submitted to the ACC: a semiconductor customer-specific contract, not a rule, so not a row. The ACC's generic inquiry into data center rate classifications is E-00000A-25-0069 (workshop 16 April 2026).

Refused or blocked (not read, not retried another way):

- https://images.edocket.azcc.gov/docketpdf/E000044076.pdf: robots.txt not readable (SSL certificate verify failed: a real hostname mismatch); not read, stays refused
- https://docket.images.azcc.gov/E000044076.pdf: robots.txt 200: DISALLOWED for ERW-research-reader, *, ClaudeBot and the other Anthropic agents
- https://s22.q4cdn.com/464697698/files/doc_downloads/2025/06/Jessica-Hobbick-Direct-Testimony-2025-Rate-Case.pdf: robots.txt answered 403: treated as disallow all
- https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000764622&type=8-K: robots.txt 200: DISALLOWED (the EDGAR archive folders were read instead)

<!-- generated: end -->
