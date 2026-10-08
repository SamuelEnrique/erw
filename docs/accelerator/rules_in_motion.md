# Rules in motion: the ten a datacenter buyer most needs to know this month

As of 2026-10-08 (UTC). Written by `warehouse/derived/rules_in_motion.py --ten --ten-doc` from the tables `large_load_rules` (public) and `large_load_rules_internal` and the model's one-line reads in `large_load_rule_reads`; nothing here is typed by hand. Method: [`docs/methods/datacenter_cost.md`](../methods/datacenter_cost.md), section "Rules in motion".

**Not legal advice, and not complete**: a docket system cannot be proved complete from outside. Federal regulators and state utility commissions only; nothing municipal. A row's sentence is the regulator's own, proved by code as a literal substring of the saved document; where it is cut from the regulator's own record of an order (a docket card, meeting minutes, a news release) and not from the order's text, the row says so. Each "read" line is **a model's read**, not the regulator's words. Where a regulator's own terms restrict copying, or no terms of it were read, this page gives the row's facts, the link to the regulator's document and the model's read, and not the sentence.

**How the ten were chosen**, by rule, from the 49 dockets with a row in motion (an open proceeding, or an order of the last 12 months), one row a docket (its newest): (1) this month first: the document is dated in the 31 days up to 2026-10-08, or the row states a deadline, hearing or effective date in the 31 days after it; (2) then how directly it sets when or at what cost a large load is served: large-load interconnection and large-load tariffs (minimum terms, collateral) before who pays for transmission, before interconnection reform at large; (3) then breadth: a federal action before a state's, more grids named before fewer; (4) then the newest. At most 2 rows a regulator. A contract or agreement with one customer is never among the ten: it sets no rule for others.

## 1. Public Utility Commission of Texas, 58481

- **What**: order; large-load interconnection; large-load tariff
- **Date**: 2026-09-18. **Status**: decided.
- **The sentence**: not shown here. The Public Utility Commission of Texas's terms ask permission to copy its text; open the document.
- **Source**: <https://interchange.puc.texas.gov/Documents/58481_218_1684654.PDF>, page 2
- **A model's read** (claude-sonnet-5-5): A large load customer must sign an intermediate agreement, make disclosures and post financial security of $50,000 per megawatt (MW) before ERCOT can include it in an interconnection study, then sign a standard agreement and pay CIAC.
- Why here: this month; directness 3; breadth 1; grids named: ERCOT.

## 2. Virginia State Corporation Commission, PUR-2025-00160

- **What**: order; large-load tariff
- **Date**: 2026-09-09. **Status**: decided.
- **The sentence**: not shown here. The Virginia State Corporation Commission's terms on copying its text were not read; open the document.
- **Source**: <https://www.scc.virginia.gov/docketsearch/DOCS/8%23%24n01!.PDF>, page 10
- **A model's read** (claude-sonnet-5-5): The Commission approves MEC's new large load rate schedule LPS-U now, with weekly billing and security deposits set by the cooperative for customers of 5,000 kW or more and 25 MW or more.
- Why here: this month; directness 3; breadth 1; grids named: PJM.

## 3. Public Utility Commission of Texas, 60332

- **What**: order; large-load tariff
- **Date**: 2026-10-02. **Status**: decided.
- **The sentence**: not shown here. The Public Utility Commission of Texas's terms ask permission to copy its text; open the document.
- **Source**: <https://interchange.puc.texas.gov/Documents/60332_9_1689557.PDF>, page 2
- **A model's read** (claude-sonnet-5-5): This opened case would let Southwestern Public Service Company, if approved, split large transmission-level customers into sub-classes and set commercial terms for them, and it directs Commission Staff to review the filing first.
- Why here: this month (the row states 2026-10-09); directness 3; breadth 0.

## 4. Public Utilities Commission of Ohio, 26-0113-EL-ATA

- **What**: order; large-load tariff
- **Date**: 2026-09-30. **Status**: decided.
- **The sentence**: not shown here. The Public Utilities Commission of Ohio's terms on copying its text were not read; open the document.
- **Source**: <https://dis.puc.state.oh.us/CaseRecord.aspx?Caseno=26-0113&link=DIVA>
- **A model's read** (claude-sonnet-5-5): The Ohio commission rejects rehearing requests from Google and two retail suppliers, leaving in place its earlier interim relief on how Ohio Power Company handles standard service offer supply for data center customers.
- Why here: this month; directness 3; breadth 0.

## 5. Public Utilities Commission of Ohio, 26-0755-EL-ATA

- **What**: order; large-load tariff
- **Date**: 2026-09-18. **Status**: open.
- **The sentence**: not shown here. The Public Utilities Commission of Ohio's terms on copying its text were not read; open the document.
- **Source**: <https://dis.puc.state.oh.us/CaseRecord.aspx?Caseno=26-0755&link=DIVA>
- **A model's read** (claude-sonnet-5-5): An Ohio judge sets October 22, 2026 for comments and November 12, 2026 for reply comments and intervention motions on Duke Energy Ohio's proposed new data center tariff, which would set terms for serving data center load.
- Why here: this month (the row states 2026-10-22); directness 3; breadth 0.

## 6. Pennsylvania Public Utility Commission, M-2026-3065062

- **What**: Secretarial Letter announcing the Technical Conference (proceeding; transmission cost allocation)
- **Date**: 2026-09-22. **Status**: "Active" (open).
- **The sentence** (cut from: notice or letter): "The Pennsylvania Public Utility Commission (Commission) will hold a Technical Conference regarding large computational load cost allocation on Tuesday, November 17, 2026 from 9:00 a.m. – 4:00 p.m. in Hearing Room 1, Commonwealth Keystone Building, 400 North Street, Harrisburg, PA 17120."
- **Source**: <https://www.puc.pa.gov/pcdocs/1950903.pdf>, page 1
- **A model's read** (claude-sonnet-5-5): The Pennsylvania PUC will hold a Technical Conference on Tuesday, November 17, 2026 on how costs are allocated to large computational loads, which may inform later cost terms for datacenters; it sets no rules itself.
- Why here: this month (the row states 2026-10-14); directness 2; breadth 0.

## 7. Federal Energy Regulatory Commission, EL26-72-000

- **What**: proceeding; large-load interconnection; transmission cost allocation
- **Date**: 2026-06-18. **Status**: open.
- **The sentence**: not shown here. The Federal Energy Regulatory Commission's terms on copying its text were not read; open the document.
- **Source**: <https://www.govinfo.gov/content/pkg/FR-2026-06-24/pdf/2026-12705.pdf>, page 1
- **A model's read**: no read yet
- Why here: not this month; directness 3; breadth 3; grids named: ISO-NE.

## 8. Federal Energy Regulatory Commission, EL26-71-000

- **What**: proceeding; large-load interconnection; transmission cost allocation
- **Date**: 2026-06-18. **Status**: open.
- **The sentence**: not shown here. The Federal Energy Regulatory Commission's terms on copying its text were not read; open the document.
- **Source**: <https://www.ferc.gov/sites/default/files/2026-06/EL26-71-000.pdf>, page 5
- **A model's read** (claude-sonnet-5-5): FERC opens a show cause proceeding that may require CAISO and its Participating Transmission Owners to add tariff rules on application, study, upgrade cost transparency, cost recovery agreements, and co-location for large loads seeking transmission service.
- Why here: not this month; directness 3; breadth 3; grids named: CAISO.

## 9. Pennsylvania Public Utility Commission, M-2025-3054271

- **What**: Opinion and Order: the petition for reconsideration of the model tariff order is withdrawn (order; large-load tariff; large-load interconnection)
- **Date**: 2026-07-16. **Status**: "ORDER ENTERED: July 16, 2026" (decided).
- **The sentence** (cut from: order text): "That the Petition for Reconsideration or Clarification filed by the Energy Association of Pennsylvania, on May 27, 2026, at Docket No. M-2025-3054271, is withdrawn."
- **Source**: <https://www.puc.pa.gov/pcdocs/1940149.pdf>, page 10
- **A model's read** (claude-sonnet-5-5): The Pennsylvania PUC grants withdrawal of the Energy Association of Pennsylvania's reconsideration petition and closes the docket, so the model tariff order stays as issued, with no new terms for large loads.
- Why here: not this month; directness 3; breadth 1; grids named: PJM.

## 10. Virginia State Corporation Commission, PUR-2026-00011

- **What**: order; large-load interconnection; interconnection reform
- **Date**: 2026-05-12. **Status**: decided.
- **The sentence**: not shown here. The Virginia State Corporation Commission's terms on copying its text were not read; open the document.
- **Source**: <https://www.scc.virginia.gov/docketsearch/DOCS/8c5b01!.PDF>, page 3
- **A model's read** (claude-sonnet-5-5): Dominion and the other participants must jointly file revised large load interconnection Standards by June 12, 2026, likely adding stronger site control and surety requirements at queue entry, a public queue database, and study timeline estimates.
- Why here: not this month; directness 3; breadth 1; grids named: PJM.
