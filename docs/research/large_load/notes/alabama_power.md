# Alabama Power Company (AL): large-load rules

Energy Research Warehouse (ERW), research pass of session 5300 (portable laptop, window P4). Method: `../README.md`.

<!-- generated: start -->

Group `southern_florida`. Rows in `utilities_<date>.csv`:

- **southern_florida-02**: Alabama PSC generic proceeding on contracts between Alabama Power and large load data center customers (Docket 33709). Status: approved (2026-10-06). License: public. Source: https://psc.alabama.gov/wp-content/uploads/2026/08/JULY-7-2026-COMMISSION-MEETING-MINUTES.pdf
  - Not published in the documents read: exit_fee, connection_timeline, queue_size.
  - Held already by window A, not repeated: threshold_mw, min_demand, contract_term, collateral.
  - Overlap with window A's registries: large_load_tariffs/alabama_act_2026_610_data_centers.yaml holds the Act's 150 MW threshold and the contract matters (minimum term, upfront payments, security and collateral, minimum payment, no figures); this row is the PSC's procedure under it, not held.
  - Notes: Status waits: news reports (abc3340, Alabama Reflector, Inside Climate News, SELC's release of 6 October 2026) say the PSC adopted final procedures on 6 October 2026: a vote within 90 days of a petition, deemed approved if the PSC does not act, a public petition with a contract summary, the full contract to the PSC and the Attorney General, no public hearing; and that Alabama Power had agreed on an interim basis to extend review from 10 to 45 days. The order itself was not found: the Docket 33709 page on psc.alabama.gov and psc.alabama.gov/?p=47744 answered 404. The October 2026 minutes were not yet found. Status updated by the 90-day pass (south-10): was 'proposed' (2026-07-07); On 6 October 2026 the Commission unanimously adopted the Docket 33709 procedures for large load data center customers as defined by Act 610: Alabama Power files a public Petition to Contract with a contract summary and gives the full contract and supporting analysis to the Commission's Legal Division and the Attorney General; each contract is approved or disapproved by Commission vote with no hearing or intervention, but is deemed approved if the Commission fails to vote within 90 days of the Petition (amended from the July proposal's 60 days); Alabama Power is to file the Petition at least 120 days before the contract would become void, and to file a compliance tariff within ten calendar days of the order's effective date.
- **southern_florida-03**: Rate HLF, High Load Factor Industrial Power (terms negotiated for loads of more than 27,000 kW). Status: in effect (2006-01-01). License: internal. Source: https://www.alabamapower.com/content/dam/alabama-power/pdfs-docs/Rates/hlf.pdf
  - Not published in the documents read: collateral, exit_fee, study_timeline, connection_timeline.
  - Overlap with window A's registries: none: large_load_tariffs/alabama_power_lpl.yaml (Rate LPL) and alabama_act_2026_610_data_centers.yaml are other rules; Rate HLF is not held.
  - Notes: A general high load factor schedule, included because it is the published tariff clause reserving negotiated terms for loads above 27 MW; the character of service clause also says the Company need not serve loads over 20,000 kVa except from transmission of 115 kV or higher. Alabama Power's Rate FCR (Flexible Contract Rate), under which news reports say data center contracts filed before 1 October 2026 were reviewed (Dotier, Alabama ADC Holdings, Woostor; contract length, minimum bill and pricing redacted), was not found: alabamapower.com/content/dam/alabama-power/pdfs-docs/Rates/FCR.pdf answered 404.

Refused or blocked (not read, not retried another way):

- https://psc.alabama.gov/docket-33709-public-comment-and-reply-info/: error: HTTP 404
- https://psc.alabama.gov/?p=47744: error: HTTP 404
- https://www.alabamapower.com/company/media-room/energy-answers/data-center-facts-for-alabama-communities/data-center-agreements-and-redactions.html: error: HTTP 404
- https://www.alabamapower.com/content/dam/alabama-power/pdfs-docs/Rates/FCR.pdf: error: HTTP 404 (Rate FCR sheet, a guessed path)

<!-- generated: end -->
