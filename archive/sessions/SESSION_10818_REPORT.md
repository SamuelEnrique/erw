# Session 10818 report (chain 740, lab-desktop window 3): electricity taxes for Illinois and Ohio, wages from the warehouse

The commits carry "Session 10817"; this report covers the work after that session's report.

- **What a reader will see once landed:** with the MWh typed, an Illinois datacenter's electricity excise tax (ten monthly blocks, $0.0033 down to $0.00202 a kWh) and an Ohio datacenter's kilowatt-hour tax (the lower of its monthly tiers and its self-assessing schedule, which a location of 45 million kWh a year may elect: $0.00257 a kWh to 500 million kWh a year, $0.001832 above). 5,000,000 MWh a year: Illinois USD 10.16 million, Ohio 9.53 million (the tiers would give 18.15 million), Virginia 4.38 million.
- **Read** (requests 306 to 312): Illinois' Department of Revenue excise rates page; Ohio's Department of Taxation instructions for distributors' returns and its self-assessing application (on dam.assets.ohio.gov, whose robots file has no rule).
- **Model:** an optional `elective` schedule on a state's electricity rule (by the year's kWh, the lower tax taken), read in the model, the downloaded Python and the replication; a third download pair (`DC_FILES_PAIR=oh-il`) and its Python test.
- **Wages:** `datacenter_wages.py --tables` reads construction from `census_cbp_construction_annual` (data request 7, built by window A) beside `census_cbp_hosting_annual`; the 51 states' figures are identical to the file chain 740 read first; the tool keeps no private read of the Bureau's files.
- **Tests:** 22 node tests (Illinois' and Ohio's hand-worked yearly taxes, Ohio below 45 million kWh on its tiers); 9 Python tests; replication 11,300 of 11,300 figures of 53 cases; the site type-checks clean.
- **Needs the key:** nothing.
- **Decisions made without you:** Ohio's buyer is assumed to elect the self-assessing schedule whenever it qualifies (decision 16); Illinois' self-assessment at 5.1 percent of price is not held (no price), so its blocks apply.
- **For Samuel's ruling:** nothing new.
