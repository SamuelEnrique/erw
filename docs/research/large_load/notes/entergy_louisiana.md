# Entergy Louisiana, LLC (LA): large-load rules

Energy Research Warehouse (ERW), research pass of session 5300 (portable laptop, window P4). Method: `../README.md`.

<!-- generated: start -->

Group `entergy`. Rows in `utilities_<date>.csv`:

- **entergy-01**: Docket U-37882: certification for Evest LLC (Meta) under the Lightning Directive, with Rider 1 to the Electric Service Agreement under Schedule LLHLFPS-L. Status: proposed (2026-03-26). License: public. Source: https://www.all4energy.org/wp-content/uploads/2026/08/2026-07-31-U-37882-AAE-UCS-Testimony-Exhibits-Edward-Burgess.pdf
  - Not published in the documents read: min_demand, contract_term, exit_fee, study_timeline, queue_size.
  - Held already by window A, not repeated: threshold_mw.
  - Overlap with window A's registries: large_load_tariffs/entergy_louisiana_llhlfps_l.yaml: the customer takes service under LLHLFPS-L (held); this row adds the customer-specific ESA and Rider 1 terms proposed in U-37882. Window A's three Entergy files were read from entergylouisiana.com and entergytexas.com, which the Entergy Corporation Site Terms cover and which bar any robot, spider or scraper (see refused): a license basis for window A to check.
  - Notes: Values are the AAE/UCS witness's summary of ELL witness Beauchamp's Table 4 (Beauchamp Direct at 18-19, HSPM/AEO) and ELL's discovery response STAFF 1-92 reproduced as an exhibit (p. 103); ELL's own application and testimony were not found on a readable host (the LPSC e-docket's document list loads by a request that answered HTTP 500). The proposal is seven CCCTs of about 5.3 GW plus three BESS (Burgess p. 10). Burgess cites the application as dated March 25, 2026; the LPSC minutes say filed March 26 and Entergy's investor page says March 27. The Sierra Club's Glick testimony (sierraclub.org) was refused. News lead only: Entergy's Q3 2026 call reportedly cited a 7 to 12 GW data center pipeline company-wide (not read in a primary document). Secondhand, kept here and not written as values (session 5300, window A's rule for intervenor quotes): the AAE/UCS witness's summary of ELL's Table 4 (testimony p. 38): "A 20-year initial term with 3-year non-renewal notice", "A minimum monthly charge intended to cover the full incremental cost to serve during the contract", "An early termination fee intended to pay all unrecovered costs"; and (pp. 47 to 48) the Meta Guaranty and the Credit Default Security on a schedule in Appendix E of the ESA. The source is the intervenor's own posted copy of its LPSC filing, not the commission's host.
- **entergy-02**: Docket U-37425: settlement customer protection conditions for the Laidley LLC (Meta) ESA served under Schedule LLHLFPS-L. Status: approved (2025-08-20). License: public. Source: https://lpscpubvalence.lpsc.louisiana.gov/portal/PSC/ViewFile?fileId=dR%2FMp4tV%2FxU%3D
  - Not published in the documents read: contract_term, study_timeline, connection_timeline.
  - Held already by window A, not repeated: threshold_mw.
  - Overlap with window A's registries: large_load_tariffs/entergy_louisiana_llhlfps_l.yaml: the ESA takes service under LLHLFPS-L (held); this row adds the settlement's customer protections.
  - Notes: The settlement states that ELL did not seek approval of the ESA and Related Agreements (term sheet p. 18). Kunkel's 15-year term and minimum-charge description are of the ESA filed with the October 2024 application; the testimony says the ESA was being renegotiated after Laidley increased its load. The term sheet also records compliance with the Industrial Load Rule (Rule 3, General Order R-34860 of 29 July 2019). The same customer's parent (Meta) is behind Evest LLC in U-37882. Secondhand, kept here and not written as values (session 5300): IEEFA witness Kunkel's direct testimony (https://ieefa.org/sites/default/files/2025-04/U-37425%20--%20Kunkel%20Direct%20Testimony%20%28as%20filed%29%20PUBLIC%20VERSION_0.pdf copy, p. 11): "The ESA is a 15-year agreement with up to three 5-year extensions (i.e. up to 30 years in total)", and the minimum monthly charges described as designed to recover the annual revenue requirements of the new infrastructure.

Refused or blocked (not read, not retried another way):

- https://www.entergy.com/terms: read once: the Entergy Corporation and subsidiaries Site Terms cover every Entergy website and bar any robot, spider, scraper or other automatic means of access, so entergy.com, entergylouisiana.com, entergyarkansas.com, entergymississippi.com, entergytexas.com, entergyneworleans.com, entergynewsroom.com and investors.entergy.com were not read for values (investors.entergy.com's regulatory page had been read once, before the terms, and was used only for docket leads)
- https://s201.q4cdn.com/714390239/files/doc_downloads/2026/03/27/E-LA-investment-to-support-customer-expansion.pdf: robots.txt answered 403: treated as disallow all (Entergy's filing highlights and investor slides host)
- https://www.sierraclub.org/sites/default/files/2026-08/u-37882-public-direct-testimony-of-devi-glick.pdf: robots.txt not readable (SSL certificate verify failed); not read
- https://www.sec.gov/cgi-bin/browse-edgar?action=getcompany&CIK=0000065984&type=8-K&dateb=&owner=include&count=40: robots.txt disallows the path for this reader and Anthropic's agents
- https://lpscpubvalence.lpsc.louisiana.gov/portal/PSC/Docket_Documents?docketId=32146: HTTP 500 (the LPSC e-docket's document list loads by a request the reader cannot make); ELL's U-37882 application and testimony therefore not found
- https://lpscpubvalence.lpsc.louisiana.gov/portal/PSC/ViewFile?fileId=0pN26I9YYZw%3d: HTTP 500 (U-37425 joint motion; the notice of settlement with the same term sheet was read instead)

<!-- generated: end -->
