# Session 10819 report (chain 740, lab-desktop window 3): states that tax no datacenter equipment

The commits carry "Session 10818"; this report covers the work after that session's report.

- **What a reader will see once landed:** with a property rate typed, a datacenter's equipment owes nothing in Iowa, Minnesota, North Dakota, Wisconsin and Kansas (as in Ohio), and Kansas's building is assessed at 25 percent. Before, the tool would have taxed the equipment at the typed rate on its cost, a tax those states do not levy.
- **Read** (requests 319 to 326): Iowa Code 427A.2 (2025: "Personal property shall not be listed or assessed for taxation and is not subject to the property tax"); Minnesota Statutes 272.02 subd. 9 (all personal property exempt but the enumerated kinds); North Dakota's Tax Commissioner ("exempts all personal property ... except that of certain oil and gas refineries and utilities"); Wisconsin's Department of Revenue on 2023 Act 12 (personal property exempt from the assessments of 1 January 2024); Kansas's 79-1439 (commercial real property at 25 percent) and 79-223 (commercial and industrial machinery and equipment bought after June 2006 exempt).
- **Not added:** Illinois and Pennsylvania (their revenue departments' pages on business equipment were looked for and not found; Illinois' statute host fails its certificate check); South Dakota (no page found).
- **Hovers kept to what was read:** "assessed at full value" (Wisconsin) was taken out of a hover as the page read does not say it.
- **Tests:** 22 node tests (each state's building and equipment worked by hand); 9 Python tests; replication 13,370 of 13,370 figures of 63 cases; 87 quotes of 34 states.
- **Needs the key:** nothing.
- **Decisions made without you:** where a state's business equipment is exempt but the building's assessment is not read, the building stays at its cost and the reader's rate (an upper bound), the equipment at nothing.
- **For Samuel's ruling:** nothing new.
