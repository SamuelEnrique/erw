# PPL Electric Utilities Corporation (PA): large-load rules

Energy Research Warehouse (ERW), research pass of session 5300 (portable laptop, window P4). Method: `../README.md`.

<!-- generated: start -->

Group `pjm_east`. Rows in `utilities_<date>.csv`:

- **pjm_east-01**: Rate Schedule LP-6, Large Load Interconnections (Electric Pa. P.U.C. No. 202, Supplement No. 2, Pages 35C to 35F). Status: in effect (2026-07-01). License: public. Source: https://www.puc.pa.gov/pcdocs/1946790.pdf
  - Not published in the documents read: study_timeline, connection_timeline.
  - Overlap with window A's registries: none held for PPL. Window A's large_load_connection_rules/pa_puc_large_load_model_tariff.yaml is the PUC's model, not PPL's tariff, and LP-6 differs from it: threshold 50 MW single or 75 MW aggregate within 10 miles at 69 kV or above (model: 50 MW individually or 100 MW aggregate); initial term at least 10 years with a ramp of up to 5 years (model: at least 5 years after a 3 to 5 year ramp)
  - Notes: LP-6 came out of PPL's base rate case settlement (Joint Petition for Non-Unanimous Settlement filed 13 March 2026, Large Load Interconnections at Joint Petition paragraphs III.I.91 to 97, per the I&E statement in support, www.puc.pa.gov/pcdocs/1918891.pdf p.13), approved as modified by the Opinion and Order entered 11 June 2026; compliance tariff filed 30 June 2026, effective 1 July 2026; replacement pages correcting typographical errors filed 27 August 2026 (the copy read). LP-6 also requires annual load forecasts to the Commission broken down by ESAs, LOAs and inquiries (p.246, Load Forecasts). Beginning 1 January 2027, $11 million a year of Universal Service Rider costs is allocated to LP-6 through a non-bypassable customer charge (pcdocs/1946790.pdf p.56). Pending, a lead not read: the Office of Consumer Advocate's complaint against PPL over data center cost allocation, Docket C-2026-3065756, filed 2 October 2026 per Governor Shapiro's petition to intervene of 15 October 2026 (pa.gov); it seeks a separate data center class and interruptible service, so LP-6 may change. PPL has not filed a tariff on the PUC's model (M-2025-3054271) that I found; the model order sets no filing date for the EDCs (pcdocs/1929842.pdf pp. 117 to 118, ordering paragraphs). PPL's own site (pplelectric.com) bars automated access in its terms of use, so its LP-6 PDF was not read.

Refused or blocked (not read, not retried another way):

- https://www.puc.pa.gov/press-release/2026/puc-issues-decision-in-ppl-electric-rate-proceeding-06042026: robots.txt not readable (URLError: SSL certificate verify failed, self-signed certificate in certificate chain); not read, not retried (later requests to www.puc.pa.gov succeeded)
- https://www.pplelectric.com/terms-of-use: PPL's terms of use bar automated access ('Do not use automated means to access this Site'); pplelectric.com not read for values (its LP-6 PDF was not opened; the PA PUC copy was used)

<!-- generated: end -->
