# Texas TSPs and DSPs in ERCOT (PUCT rule) (TX): large-load rules

Energy Research Warehouse (ERW), research pass of session 5300 (portable laptop, window P4). Method: `../README.md`.

<!-- generated: start -->

Group `texas`. Rows in `utilities_<date>.csv`:

- **texas-01**: 16 TAC §25.194, Large Load Interconnection Standards (PUCT Project No. 58481), adopted 18 September 2026, effective 8 October 2026: intermediate agreement, study fee, financial security, standard large load interconnection agreement (SLLIA), CIAC, withdrawal, forfeiture and reallocation terms. Status: in effect (2026-10-08). License: public. Source: https://interchange.puc.texas.gov/Documents/58481_218_1684656.PDF
  - Not published in the documents read: queue_size.
  - Overlap with window A's registries: Not held. large_load_connection_rules/puct_project_58000_proposal.yaml is the separate tariff rulemaking (proposed amendments to 25.192 and 25.193 and new 25.252: 20-year agreement, 240 payments); it is still pending (the latest filing in Project 58000, item 70 of 1 October 2026, is comments on the minimum billing demand study), and §25.194 relies on its §25.193 minimum billing demand. ercot_planning_guide_section_9.yaml and ercot_large_load_batch_update_april_2026.yaml hold ERCOT's own Batch Zero clocks and threshold; §25.194(h) sets the PUCT's return and forfeiture terms for batch zero load, which those files do not hold.
  - Notes: The rule binds electric utilities, municipally owned utilities and electric cooperatives interconnecting large loads to the ERCOT system (subsection (a)); a municipally owned utility or cooperative may add its own requirements: 'Nothing in this section limits the authority of a municipally owned utility or an electric cooperative to impose electric service requirements for large load customers on their systems in addition to the standards adopted under this section' (page 25). Also in the rule, not entered as fields: required disclosures under both agreements (site control with a lease of at least five years, substantially similar requests elsewhere in Texas, water, backup generation, power supply, controllable load resource), audit and verification by ERCOT and commission staff with forfeiture and reallocation for false information (subsections (j), (k)), and the transition for customers that signed a §25.370(g) agreement (subsection (i)). A batch zero load with an interconnection agreement signed on or before 1 June 2025 pays direct interconnection costs under that agreement (subsection (h)(3)(B), page 65). The Texas Register's own pages were not read (sos.state.tx.us answered 403 on the October 9 issue; the adoption was submitted for the issue of 2 October 2026).

<!-- generated: end -->
