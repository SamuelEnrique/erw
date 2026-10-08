# Tags of the policy actions held

`policy_action_tags` (session 154) says which of the policy actions held in `policy_actions` touch one of four things
a large load cares about: **large loads**, **interconnection**, **transmission cost**, **tax credits**. It is one row
for each action and tag, with the term that matched and the field it matched in, so that a person can redo any row
by eye. The tags are made by a written rule that code applies. No model reads a row and no request is made.

- Code: `warehouse/derived/policy_action_tags.py`
- The rule, as the code reads it: `warehouse/config/policy_tag_rules.json` (version 2)
- Input: `policy_actions` (1,843 actions on 8 October 2026: Federal Register documents of FERC, the Department of
  Energy, EPA, the NRC, the Bureau of Land Management and Interior since 1 October 2025, and news releases of the
  NRC, the Department of Energy, the Texas commission and the California commission)
- Output: `policy_action_tags`, events shape, `event_type` `policy_tag`, a snapshot (a later rule replaces the rows)

## The rule

**How a row is read.** The title and the abstract of the action, each on its own: lower case, every hyphen and dash
a space, white space collapsed. Company names that hold a topic word are taken out first ("PJM Interconnection",
"Eastern Interconnection", "Western Interconnection", "Texas Interconnection"): a name is not a topic. A term matches
when its words stand in the text as whole words, in order. The docket is read for exclusions and for the dockets
listed by number. The agency and the action type are recorded on every row; an action of an agency outside the list
(federal: FERC, DOE, EPA, NRC, BLM, Interior; state: the Texas and California commissions) is never tagged.

**Nothing municipal.** An action whose title or abstract holds one of these phrases is about municipal permitting,
zoning or a local hearing and is never tagged, whatever else it says: zoning, rezoning, city council, county board,
county commission, county commissioners, board of supervisors, planning commission, town board, township board,
building permit, conditional use permit, special use permit, local hearing, municipal permit, local permit.

| Tag | Terms (title or abstract) | What keeps an action out of the tag |
|---|---|---|
| `large_load` | large load(s); data center(s); datacenter(s); large power user(s); large electricity user(s); large electric customer(s); large customer(s); co located load(s); colocated load; co location; colocation; hyperscale, hyperscaler(s); large flexible load(s); load growth; demand growth | "large electric generating unit(s)" (a generator, not a load) |
| `interconnection` | interconnection(s); interconnect, interconnected, interconnecting; interconnection queue; queue reform | pipeline(s), natural gas, liquefied, LNG, gas transmission, telecommunications, broadband, fiber optic in the title or abstract; a FERC docket that begins CP, RP, PF, IS or OR (gas and oil pipelines); a docket that holds "-LNG" |
| `transmission_cost` | cost allocation (with "transmission" in the title or abstract); transmission formula rate(s); transmission rate(s); transmission cost(s); transmission charge(s); transmission access charge; transmission service rate(s); transmission revenue requirement; transmission incentive(s); network upgrade(s); formula rate(s) (with "transmission service", "transmission formula" or "transmission rate"); transmission (with "electricity customers", "ratepayer(s)", "customer bills" or "who pays") | pipeline(s), natural gas, gas transmission, liquefied; the same gas and oil docket prefixes. A transmission line's siting or environmental review is not a cost action: "transmission" alone tags nothing |
| `tax_credit` | tax credit(s); investment tax credit; production tax credit; clean electricity investment credit; clean electricity production credit; energy credit (with "tax", "internal revenue" or "section 48"); section 45, 45Y, 45X, 45Q, 45V, 45U, 45Z, 48, 48C, 48E; beginning of construction (with "credit" or "tax"); prohibited foreign entity; foreign entity of concern (with "credit" or "tax"); elective pay; direct pay (with "credit" or "tax") | climate credit(s) (California's bill credit), credit rating, emission(s) credit, renewable energy certificate. "Credit" alone tags nothing |

**Dockets listed by number.** Some notices carry only the names of the parties in their title and have no abstract,
so no term can match. Where the docket of such a notice is a proceeding whose own order was read (the rule file
lists each docket with the order's address and the grid operator it is about), the notice takes that proceeding's
tags; the matched field is `docket` and the matched term is the docket number. Nine dockets are listed, all FERC's:
EL26-67 to EL26-72 (the proceedings of 18 June 2026 on each operator's tariff provisions for interconnecting large
loads), EL25-49 (co-located load in PJM), ER26-247 (SPP's high impact large loads) and RM26-4 (the interconnection
of large loads). A notice whose docket field lists more than three docket numbers is a combined notice (a notice of
staff attendance at a meeting lists every docket that may be spoken of) and takes no docket's tags.

## What the rule tags (8 October 2026)

1,843 actions read, **14 tagged, 30 rows**: `large_load` 10, `interconnection` 8, `transmission_cost` 12,
`tax_credit` 0. Eight of the 14 are FERC's notices in dockets EL26-67 to EL26-72, tagged by docket with all three
tags; six are tagged by a term (four federal: Order No. 1920's extension of time, the workshop on transmission
formula rates, the notice of staff attendance at the conference on emerging large loads, Rate Order No. WAPA-211;
two state releases: the Texas commission's on ERCOT's process for data centers, the California commission's on its
transmission advocacy). 12 of the 14 are federal; all 14 are of the last 12 months.

## The rule measured: 40 and 40

Drawn by `random.Random(154)` over the sorted event ids, the tagged first (`--sample 40 --seed 154`), and read by
the session's agent, row by row.

- **Tagged.** Version 1 tagged 7 actions, fewer than 40, so all 7 were read. All 7 touch the topic by the tag's own
  definition (7 of 7). Two of them, the two notices of Rate Order No. WAPA-222, are the rates of a balancing
  authority's ancillary services (scheduling, reserves, imbalance): inside the letter of "formula rates" beside
  "transmission", outside what transmission costs. Counted strictly, 5 of 7.
- **Untagged.** 40 of 40 are rightly untagged (hydropower licenses, gas pipeline certificates, reactor licensing,
  efficiency standards, oil and gas leasing). The sample found no miss. Forty rows with no miss do not show there is
  none: by the rule of three they are consistent with a miss rate of up to about 7 in 100.
- **What the rule misses, found outside the sample.** Reading the scorer's one-line note on every action (the `why`
  column, written by a model in an earlier session; used here only to look for misses, never to tag) turned up:
  the California commission's release "Protecting California Electricity Customers - CPUC Transmission Advocacy at
  FERC" (transmission cost; its title holds no cost word); and the notices in FERC dockets EL26-67 to EL26-72, whose
  titles are only the names of an operator and its transmission owners.
- **The one correction (version 2).** (a) "formula rate(s)" now needs "transmission service", "transmission formula"
  or "transmission rate" beside it, not the bare word "transmission": the two WAPA-222 notices leave. (b) "transmission"
  with "electricity customers", "ratepayer(s)", "customer bills" or "who pays" now tags: the California release
  enters. (c) The dockets listed by number, above. After the correction every tagged action was read again: 14 of
  14 touch their tag's topic (the eight docket notices by the proceeding's own order; the notice of staff attendance
  is of little weight but is about large loads). The untagged sample drawn again under version 2 shares 18 of its
  40 rows with the first; the 22 new ones were read too: none is a miss. 62 untagged actions read in all, no miss.
- **Tax credits: no action held.** No title or abstract of the 1,843 holds a tax credit term. The six federal
  agencies read do not include the Treasury or the Internal Revenue Service, where the credit rules are published;
  the tag is empty because the table lacks the publisher, not because nothing is in motion.
- **What the rule cannot see.** It reads a title and an abstract. 834 of the 865 FERC actions held have no abstract, and a
  title such as "Combined Notice of Filings" or a utility's name says nothing of its subject.

## What the tags are not

Not a reading of the document, not a judgment of its weight, and not complete. Nothing municipal. The table's tier
in `coverage.csv` is `model_extracted` because its input, `policy_actions`, carries a model's scores; the tags use
none of those columns.
