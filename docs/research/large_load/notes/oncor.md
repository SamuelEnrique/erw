# Oncor Electric Delivery Company LLC (TX): large-load rules

Energy Research Warehouse (ERW), research pass of session 5300 (portable laptop, window P4). Method: `../README.md`.

<!-- generated: start -->

Group `texas`. Rows in `utilities_<date>.csv`:

- **texas-02**: Large-load (75 MW or more) interconnection with Oncor: the Transmission/Substation Facility Extension Agreement of its Tariff for Retail Delivery Service (6.3.2, Docket 58306) and 6.2.3.6 (transmission voltage), Batch Zero customer agreements and security, and 16 TAC §25.194 (effective 8 October 2026; its terms are in the statewide row of this file). Status: in effect (2026-10-08). License: public. Source: https://www.sec.gov/Archives/edgar/data/1193311/000119331126000026/c311-20260930x10q.htm
  - Held already by window A, not repeated: min_demand.
  - Overlap with window A's registries: large_load_tariffs/oncor_transmission_service.yaml: the delivery schedule (80% ratchet, same value, written held); its docket field reads 'not printed for the base rates', while the PUCT's stamped copy of the same tariff prints 'Docket: 58306' and 'Approved on: APR 17 2026' on its sheets and Oncor's 10-Q says the new base rates took effect 1 June 2026 (a correction for window A to check). large_load_connection_rules/ercot_planning_guide_section_9.yaml and ercot_large_load_batch_update_april_2026.yaml hold Batch Zero itself; 16 TAC §25.194 is the statewide row of this file.
  - Notes: Oncor's tariff (Docket 58306) has no large-load schedule or section: a large load uses Transmission Service, the Facilities Extension Policy (5.7), 6.2.3.6 and the 6.3.2 agreement form; the 6.3.5 Discretionary Service Agreement form (page 182 of oncor.com's copy) leaves term and services blank. Lead, not a value: the complaint of ACS DC Hicks Field Road LLC against ERCOT (PUCT Docket 60425, the copy ERCOT posts at https://www.ercot.com/files/docs/2026/10/26/60425-Complaint-of-ACS-DC-Hicks-Field-Road-LLC-Against-ERCOT.pdf) describes one Oncor Facility Extension Agreement requiring financial security within ten business days of execution; customer-specific. Oncor's 8-K Exhibit 99.1: a final transmission plan reflecting Batch Zero is not expected until fall of 2027 (the 10-Q: second half of 2027); classifications conditional on an ERCOT audit expected in December 2026. Customer cash deposits were about $580 million on 31 October 2026 (10-Q).

<!-- generated: end -->
