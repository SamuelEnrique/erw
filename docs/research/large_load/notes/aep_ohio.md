# Ohio Power Company (AEP Ohio) (OH): large-load rules

Energy Research Warehouse (ERW), research pass of session 5300 (portable laptop, window P4). Method: `../README.md`.

<!-- generated: start -->

Group `aep`. Rows in `utilities_<date>.csv`:

- **aep-01**: Schedule DCT (Data Center Tariff), P.U.C.O. No. 22, 1st Revised Sheets 223-1 to 223-8. Status: in effect (2026-08-28). License: internal. Source: https://www.aepohio.com/lib/docs/ratesandtariffs/Ohio/November_2026_Ohio_Power_Tariff_Book.pdf
  - Held already by window A, not repeated: threshold_mw, min_demand, collateral.
  - Overlap with window A's registries: large_load_tariffs/aep_ohio_schedule_dct.yaml: threshold, min_demand and collateral held with the same values (same November 2026 tariff book). contract_term adds the four-year ramp cap and the three-year notice to the held term (Load Ramp Period plus 8 years); exit_fee, study_timeline, connection_timeline and queue_size are new.
  - Notes: 2026 change: the 1st Revised sheets (effective 28 August 2026) add Interim Procedures from the 5 August 2026 Finding and Order in 26-113-EL-ATA: no less than 180 days' advance written notice to return to or start on SSO, with a separate procurement at the customer's cost (Sheet 223-5, PDF p. 117). AEP company-wide pipeline (public, SEC Form 8-K Exhibit 99.1, 28 October 2026, https://www.sec.gov/Archives/edgar/data/4904/000000490426000069/a3q20268kpressreleaseex991.htm): 'With 15 gigawatts (GW) of new load commitments signed during the third quarter, AEP’s incremental contracted load is expected to grow to 84 GW by 2031. Projects are only included as incremental contracted load if backed by fully executed electric service agreements or letters of agreement.' (not stated per company). AEP 10-Q for Q3 2026 (https://www.sec.gov/Archives/edgar/data/4904/000000490426000072/aep-20260930.htm): OHTCo, OPCo and a customer signed agreements in August 2026 for three 765 kV lines to support 'a proposed 10.4 GW data center campus in Piketon, Ohio'. Leads, not verified: OMAEG's appeal of the DCT order is Supreme Court of Ohio Case No. 2025-1458 (news and OMA releases); the court's docket was refused (robots not readable). AEP Ohio's February 2026 Update, the Stipulation and the Opinion and Order sit on dis.puc.state.oh.us (reCAPTCHA, not tried); the February 2026 Update reportedly also gives 12,219 MW signed before the tariff (news, unverified).
- **aep-02**: PUCO Opinion and Order in Case No. 24-508-EL-ATA adopting the 10/23 Stipulation (Schedule DCT terms), as modified. Status: approved (2025-07-09). License: public. Source: https://www.psc.state.fl.us/library/FILINGS/2025/07142-2025/07142-2025.pdf
  - Not published in the documents read: connection_timeline.
  - Overlap with window A's registries: large_load_tariffs/aep_ohio_schedule_dct.yaml (internal, the tariff sheets on aepohio.com): the order prints the same 25 MW threshold, 85 percent minimum, Load Ramp Period plus eight years, 50/65/80/90 percent ramp floors and 50 percent collateral; this public commission-hosted copy can serve as the public source for them.
  - Notes: The order's summary is a two-column comparison of the 10/10 and 10/23 Stipulations; every quote here is from the 10/23 (adopted) column or the Commission's own findings. The order also directs AEP Ohio 'to cease its temporary service moratorium, consistent with this Order' (para. 158) and records that the moratorium in central Ohio began in March 2023 (para. 45).

Refused or blocked (not read, not retried another way):

- https://www.supremecourt.ohio.gov/clerk/ecms/#/caseinfo/2025/1458: not retried: a script-built case search page (hash route), not a document page; the first attempt failed only on a certificate check of robots.txt
- https://dis.puc.state.oh.us/ViewImage.aspx?CMID=A1001001A26B12B61453D00940: not tried: PUCO docketing has a reCAPTCHA (AEP Ohio's February 2026 Update; also the Stipulation and the Opinion and Order linked from the DCT page)

<!-- generated: end -->
