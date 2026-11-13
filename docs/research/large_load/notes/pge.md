# Pacific Gas and Electric Company (CA): large-load rules

Energy Research Warehouse (ERW), research pass of session 5300 (portable laptop, window P4). Method: `../README.md`.

<!-- generated: start -->

Group `southwest_california`. Rows in `utilities_<date>.csv`:

- **southwest_california-01**: Electric Rule No. 30, Retail Service Transmission Facilities, Interim Implementation (50 kV to 230 kV). Status: in effect (2025-12-04). License: public. Source: https://www.pge.com/tariffs/assets/pdf/tariffbook/ELEC_RULES_30.pdf
  - Not published in the documents read: min_demand, contract_term, study_timeline, connection_timeline.
  - Overlap with window A's registries: large_load_connection_rules/pacific_gas_and_electric_electric_rule_30.yaml holds the same interim Rule 30 (Advice 7772-E, effective 2025-12-04) as four timed steps; no held value differs. This row adds the collateral, exit and queue fields.
  - Notes: Final Rule 30 still pending in A.24-11-007 on 13 November 2026: the ALJ ruling of 7 August 2026 (docs.cpuc.ca.gov/PublishedDocs/Efile/G000/M613/K880/613880295.PDF) reopened the record for comments on FERC's show cause order (EL26-71), reply comments due 4 September 2026, after which the record is submitted; no proposed or final decision was found. A partial settlement of 7 May 2026 (PG&E, Cal Advocates, CalCCA, Sierra Club) covers information sharing only (per AReM and Shell's comments, docs.cpuc.ca.gov/PublishedDocs/Efile/G000/M608/K211/608211962.PDF). Customer-specific transmission-level agreements are approved by resolution: draft Resolution E-5455 of 16 July 2026 (Google, 250 MW at 230 kV, San Jose; docs.cpuc.ca.gov/PublishedDocs/Published/G000/M607/K718/607718746.PDF) limits annual refunds to 100 percent of annual net revenues and says Resolutions E-5420, E-5433 and E-5439 limited them to 75 percent; refunds are not one of the eight fields. Refused: the CPUC proceeding page (apps.cpuc.ca.gov, robots) and PG&E's investor PDF host (s21.q4cdn.com, robots 403); the same presentation was read from the SEC copy. The pipeline counts data center load of 20 MW or more at any voltage, not only Rule 30 applicants.

Refused or blocked (not read, not retried another way):

- https://apps.cpuc.ca.gov/apex/f?p=401:56:0::NO:RP,57,RIR:P5_PROCEEDING_SELECT:A2411007: robots.txt 200: DISALLOWED for ERW-research-reader, *, ClaudeBot, Claude-User, Claude-Web, Claude-SearchBot, anthropic-ai
- https://s21.q4cdn.com/673114418/files/doc_financials/2026/q3/Q3-26-Earnings-Presentation.pdf: robots.txt answered 403: treated as disallow all (the same presentation was read from sec.gov)

<!-- generated: end -->
