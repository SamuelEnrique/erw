# AEP Texas Inc. (TX): large-load rules

Energy Research Warehouse (ERW), research pass of session 5300 (portable laptop, window P4). Method: `../README.md`.

<!-- generated: start -->

Group `texas`. Rows in `utilities_<date>.csv`:

- **texas-03**: Large-load interconnection under the PUCT's Large Load Interconnection Standards (Texas Administrative Code, adopted September 2026, effective October 2026) and ERCOT Batch Zero: intermediate agreement, $50,000 per MW security, standardized interconnection agreement, as AEP's Q3 2026 10-Q states for AEP Texas. Status: in effect (2026-10). License: public. Source: https://www.sec.gov/Archives/edgar/data/4904/000000490426000072/aep-20260930.htm
  - Not published in the documents read: min_demand, study_timeline, connection_timeline.
  - Overlap with window A's registries: large_load_connection_rules/ercot_planning_guide_section_9.yaml and ercot_large_load_batch_update_april_2026.yaml hold Batch Zero itself; large_load_connection_rules/puct_project_58000_proposal.yaml holds the separate Project 58000 tariff proposal (20-year agreements). The adopted interconnection standards (16 TAC 25.194 by the leads) are not held; this row records them only as AEP describes them.
  - Notes: AEP Texas's own tariff (aeptexas.com, Tariff for Electric Delivery Service effective 5 January 2026) answered HTTP 404 and was not read; no AEP Texas large-load schedule is named in the 10-Q. The 10-Q: in August 2026 the Governor directed a verification of Batch Zero loads and an audit of data center projects 25 MW and above; ERCOT 'has currently paused Batch Zero classification and study activity and stated it will not authorize large loads to energize until verification is complete.' The adopted rule's text was not read (PUCT and Texas Register hosts failed the reader's TLS check).

Refused or blocked (not read, not retried another way):

- https://interchange.puc.texas.gov/search/filings/?UtilityType=A&ControlNumber=58481&ItemMatch=Equal&DocumentType=ALL&SortOrder=Ascending: robots.txt not readable (URLError: SSL CERTIFICATE_VERIFY_FAILED, unable to get local issuer certificate); not read
- https://interchange.puc.texas.gov/Documents/58481_4_1543628.PDF: robots.txt not readable (URLError: SSL CERTIFICATE_VERIFY_FAILED, unable to get local issuer certificate); not read
- https://www.puc.texas.gov/agency/rulesnlaws/subrules/electric/Electric.aspx: robots.txt not readable (URLError: SSL CERTIFICATE_VERIFY_FAILED, unable to get local issuer certificate); not read
- https://www.sos.state.tx.us/texreg/archive/October92026/Adopted%20Rules/16.ECONOMIC%20REGULATION.html: robots.txt not readable (URLError: SSL CERTIFICATE_VERIFY_FAILED, self-signed certificate in certificate chain); not read
- https://www.sos.state.tx.us/texreg/archive/October162026/Adopted%20Rules/16.ECONOMIC%20REGULATION.html: robots.txt not readable (URLError: SSL CERTIFICATE_VERIFY_FAILED, self-signed certificate in certificate chain); not read
- https://www.sos.texas.gov/texreg/archive/July242026/Proposed%20Rules/16.ECONOMIC%20REGULATION.html: robots.txt not readable (URLError: SSL CERTIFICATE_VERIFY_FAILED, self-signed certificate in certificate chain); not read
- https://www.aeptexas.com/lib/docs/ratesandtariffs/Texas/AEPTEXASTARIFFEffJan5-2026.pdf: HTTP 404 (no robots file)

<!-- generated: end -->
