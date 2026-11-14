# Interstate Power and Light Company (Alliant Energy) (IA): large-load rules

Energy Research Warehouse (ERW), research pass of session 5300 (portable laptop, window P4). Method: `../README.md`.

<!-- generated: start -->

Group `xcel_plains`. Rows in `utilities_<date>.csv`:

- **xcel_plains-08**: Individual customer rate (ICR) tariff and the IUC-approved ICRs for data centers. Status: approved (2024-09). License: public. Source: https://www.sec.gov/Archives/edgar/data/352541/000035254126000007/lnt-20251231.htm
  - Not published in the documents read: threshold_mw, min_demand, contract_term, collateral, exit_fee, study_timeline, connection_timeline.
  - Notes: The ICR tariff sheet and the IUC's ICR orders were not read (IUC EFS disallows all robots; alliantenergy.com robots answered 403). The 10-K says IPL has ESAs with two new data center customers and WPL with one. The 10-Q says a WPL data center customer moved to a site in IPL's territory in Q1 2026 and its ESA was renegotiated. The IUC's newsroom (iuc.iowa.gov) shows no large-load release in 2025 or 2026. Status date as the reading group wrote it: '2024-09 (IUC rate review order creating the ICR tariff); ICRs for data centers approved May 2025 and October 2025; a further ICR request filed October 2026, decision expected Q1 2027'.

Refused or blocked (not read, not retried another way):

- https://efs.iowa.gov/efs/: robots.txt 200: DISALLOWED for every agent (the IUC's electronic filing system, which holds tariffs and orders)
- https://www.alliantenergy.com/: robots.txt answered 403: treated as disallow all

<!-- generated: end -->
