# Oncor Electric Delivery Company LLC (TX): large-load rules

Energy Research Warehouse (ERW), research pass of session 5300 (portable laptop, window P4). Method: `../README.md`.

<!-- generated: start -->

Group `texas`. Rows in `utilities_<date>.csv`:

- **texas-01**: Large-load (75 MW or greater) transmission interconnection: customer financial security and Batch Zero customer agreements, under ERCOT's Batch Zero and the PUCT's large load interconnection standards adopted September 2026, as Oncor's SEC filings state (the delivery schedule such a load takes is Transmission Service, held by window A). Status: in effect (2026-10). License: public. Source: https://www.sec.gov/Archives/edgar/data/1193311/000119331126000026/c311-20260930x10q.htm
  - Not published in the documents read: contract_term, exit_fee, study_timeline, connection_timeline.
  - Held already by window A, not repeated: min_demand.
  - Overlap with window A's registries: large_load_tariffs/oncor_transmission_service.yaml: the delivery schedule (80% ratchet, same value, written held); its docket field reads 'not printed for the base rates', while Oncor's Q3 2026 10-Q names PUCT Docket No. 58306 as the base rate review whose new rates took effect 1 June 2026 (a correction for window A to check). large_load_connection_rules/ercot_planning_guide_section_9.yaml and ercot_large_load_batch_update_april_2026.yaml hold the Batch Zero process itself (75 MW, ERCOT's clocks); this row adds only Oncor's own security terms and queue.
  - Notes: Not read: Oncor's Tariff for Retail Delivery Service (its Section 6.3.2 form of Transmission/Substation Facility Extension Agreement and its Discretionary Service Agreement) on www.oncor.com: the reader's TLS check failed ('self-signed certificate in certificate chain'), so the host was not read. Lead, not a value: the complaint of ACS DC Hicks Field Road LLC against ERCOT (PUCT Docket 60425, the copy ERCOT posts at https://www.ercot.com/files/docs/2026/10/26/60425-Complaint-of-ACS-DC-Hicks-Field-Road-LLC-Against-ERCOT.pdf) describes one Oncor Facility Extension Agreement requiring financial security within ten business days of execution and a Discretionary Services Agreement backed by security; customer-specific, so not entered as a rule. Oncor's 8-K Exhibit 99.1 says a final transmission plan reflecting Batch Zero is not expected until fall of 2027 (the 10-Q says the second half of 2027) and that the classifications are conditional on an ERCOT audit expected in December 2026. Customer cash deposits were about $580 million on 31 October 2026 (10-Q). The adopted 16 TAC 25.194 text (PUCT Project 58481) was not read: interchange.puc.texas.gov, www.puc.texas.gov and the Texas Register (sos.state.tx.us) all failed the reader's TLS check.

Refused or blocked (not read, not retried another way):

- https://www.oncor.com/content/dam/oncorwww/documents/about-us/regulatory/tariff-and-rate-schedules/Tariff%20for%20Retail%20Delivery%20Service.pdf.coredownload.pdf: robots.txt not readable (URLError: SSL CERTIFICATE_VERIFY_FAILED, self-signed certificate in certificate chain); not read
- https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0001193311&type=8-K&dateb=&owner=include&count=10: robots.txt 200: DISALLOWED for every agent (the EDGAR Archives path, which robots allows, was used instead)

<!-- generated: end -->
