# Georgia Power Company (GA): large-load rules

Energy Research Warehouse (ERW), research pass of session 5300 (portable laptop, window P4). Method: `../README.md`.

<!-- generated: start -->

Group `southern_florida`. Rows in `utilities_<date>.csv`:

- **southern_florida-01**: Rules and Regulations for Electric Service A1, D13 and D14 (customers of 100 MW or more) and the Large Load Contract Review Process (Docket 44280). Status: in effect (date not published). License: public. Source: https://services.psc.ga.gov/api/v1/External/Public/Get/Document/DownloadFile/220667/101841
  - Not published in the documents read: connection_timeline.
  - Held already by window A, not repeated: threshold_mw, min_demand, collateral.
  - Overlap with window A's registries: large_load_tariffs/georgia_power_rules_100mw.yaml holds threshold (100 MW), min_bill, collateral and exit_fee (D14 text) from the same December 2024 filing, effective 2025-02-01; this row adds contract_term (Commission release), the 26 August 2026 joint statement on termination, the 30-day contract review and the queue. large_load_tariffs/georgia_power_tou_sc_15.yaml (Monthly Access Charge option, 100 MW, term three years or as the CES specifies) is the schedule these customers take and is not repeated here.
  - Notes: The Commission's orders of 28 January 2025 (document 221165) and 17 April 2025 (document 222325, which sets the minimum bill framework) are served as .docx files that the reader cannot turn into text, and the April order's PDF copy (222325/103476) is a scan with no text layer: their wording (minimum bill at the higher of tariffed rates or the minimum bill, liability for minimum bills over the remaining term) is not cited. The 26 August 2026 joint statement says Staff had reviewed six prior Large Load contracts and did not object to the seventh (filed 27 July 2026, reported in news as OpenAI, 3,200 MW); it promises a semi-annual Large Load Data Center report and a public summary of each contract filed. An intervenor brief (GIPL and Southface, 16 Dec 2025, Docket 56298/56310, document 224874) says the contracts carry a two-year termination notice and minimum bills for two years after termination, citing hearing testimony: a party's characterization, lead only. The Q2 2026 and Q3 2026 pipeline reports were not found; Southern Company's investor files (s27.q4cdn.com) were refused by robots; the PSC facts site gave a bot check. The 2025 certification stipulation (Docket 56298/56310, document 224772) sets a minimum large load revenue forecast and a load flexibility collaboration, not connection terms. Lead (news only): a Nuclear Uprate tariff NU-1 filed 21 September 2026 in Docket 44280 for Google's subscription; not a connection rule, not read. Corrected by the independent audit of session 5304 (A-12): the status date was '2025-02-01', read from the footer of the Rules pages as proposed in the December 2024 filing ('Paragraphs 13 and 14 added February 1, 2025'); the Commission's order of 28 January 2025 approves the revisions as modified by Staff and prints no effective date, and the adopted compliance pages (the order of 17 April 2025, a scan) were not read, so the date is not published.

Refused or blocked (not read, not retried another way):

- https://psc.ga.gov/search/facts-docket/?docketId=55378: blocked: the answer looks like a bot check; not retried
- https://s27.q4cdn.com/273397814/files/doc_financials/2026/q3/SO-2026-Q3-Earnings-Call-Final.pdf: refused: robots.txt answered 403, treated as disallow all (Southern Company investor files)
- https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000092122&type=10-Q&dateb=&owner=include&count=10: refused: robots.txt disallows the path
- https://services.psc.ga.gov/api/v1/External/Public/Get/Document/DownloadFile/221165/102330: error: served as .docx; the reader keeps no text (Order Approving Revisions, January 2025)
- https://services.psc.ga.gov/api/v1/External/Public/Get/Document/DownloadFile/222325/103476: no_text: the PDF has no text layer (scan of the April 2025 compliance order); the .docx copy 222325/103475 was not requested
- https://services.psc.ga.gov/api/v1/External/Public/Get/Document/DownloadFile/224483/105760: error: served as .docx; the reader keeps no text
- https://services.psc.ga.gov/api/v1/External/Public/Get/Document/DownloadFile/224953/106187: error: served as .docx; the reader keeps no text
- https://services.psc.ga.gov/api/v1/External/Public/Get/Document/DownloadFile/226607/107927: error: served as .docx or .xlsx; the reader keeps no text (Q1 2026 report attachment)

<!-- generated: end -->
