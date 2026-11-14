# Nevada Power Company and Sierra Pacific Power Company (NV Energy) (NV): large-load rules

Energy Research Warehouse (ERW), research pass of session 5300 (portable laptop, window P4). Method: `../README.md`.

<!-- generated: start -->

Group `southwest_california`. Rows in `utilities_<date>.csv`:

- **southwest_california-05**: Form Large Load Electric Service Agreement (LLESA) and Form Framework Agreement, filed for PUCN approval with the 2026 Joint IRP. Status: proposed (2026-05-07). License: public. Source: https://www.nvenergy.com/publish/content/dam/nvenergy/brochures_arch/about-nvenergy/rates-regulatory/recent-regulatory-filings/2026-irp/NPC-SPPC-Volume-2.pdf
  - Not published in the documents read: study_timeline, connection_timeline.
  - Held already by window A, not repeated: threshold_mw.
  - Overlap with window A's registries: large_load_tariffs/nv_energy_llesa.yaml (the June 2026 fact sheet): status 'framework' with effective 2026-06-01 differs, the form LLESA is proposed and pending in PUCN Docket 26-05007 (filed 2026-05-07 per the PUCN, application dated 2026-05-06, statutory deadline 2026-12-02, no order found); the fact sheet printed no minimum share, term, security or exit figure, which this row adds from the form. Threshold (25 MW) matches and is held.
  - Notes: PUCN record read on 13 November 2026 (pucweb1.state.nv.us, on the coordinator's retry after the certificate fix): the docket list (26-05007 dated 05/07/2026; the customer LLESA dockets 26-05026, 26-05027, 26-05029 and 26-05030 dated 05/29/2026, and 26-05028 dated 06/03/2026) and the calendar (hearings in 26-05007 on 26 to 29 October and 16 to 20 November 2026, Phase 3 rebuttal testimony due 2 November 2026). No order, stipulation or hearing transcript was found: the PUCN's docket detail and document search open only through form postbacks, which this GET-only reader cannot follow, and puc.nv.gov's /uploadedFiles/ newsletters are barred by its robots file. Which phase carries the form LLESA is not stated in a PUCN document read (a lead, the Nevada Conservation League's tracker, puts large-load cost responsibility in Phase 2). The form adds rate components to bundled Schedule LGS-3 / GS-3 (Wells Direct p. 109). The Companies asked for a deemed approved date of 18 September 2026 for the form (p. 7). Leads (news, not written): PUCN Staff recommended rejecting the form in its current form and opening a separate proceeding; Microsoft's rebuttal of 16 October 2026 asked for a replacement large-load tariff. Customer redlines in the same exhibit reserve positions on the 90 percent minimums and the security (Exhibit G). Clean Transition Tariff: the CTT orders of Dockets 24-05022 and 24-05023 required an exemplar CTT pricing model in an IRP, filed here as Exhibits Wells-Direct-4 and -5 (p. 126); the CTT sheets were not found (nvenergy.com CTT_North.pdf answered 404), so no CTT row. Schedule LGS-X (closed) is held in large_load_tariffs/nv_energy_nevada_power_lgs_x.yaml.

Refused or blocked (not read, not retried another way):

- https://www.nvenergy.com/publish/content/dam/nvenergy/brochures_arch/about-nvenergy/rates-regulatory/electric-schedules-north/CTT_North.pdf: HTTP 404 (a guessed path; the CTT sheet was not found)
- https://puc.nv.gov/uploadedFiles/pucnvgov/Content/About/Media_Outreach/PUCNConnection/NewsletterOctober2026.pdf: robots.txt 200: DISALLOWED for ERW-research-reader, *, ClaudeBot, Claude-User, Claude-Web, Claude-SearchBot, anthropic-ai (the September 2026 newsletter likewise)

<!-- generated: end -->
