# The deal rows, sorted by who stands behind them: 23 October 2026

Energy Research Warehouse (ERW), session 821 (chain `queue/done/080-night-23-october-portable-landing-deals-.md`, portable-laptop). Every figure is the output of `warehouse/deals/public_rows.py --markdown`, read from `energy_deals` (505 rows, extracted 2026-10-22T15:02:19Z) and `energy_deals_evidence` (557 rows, the same run) as `scripts/sync.py --check` found them current with the warehouse of record on this machine at 07:45 UTC. No row's data changed; no request was made.

## Read these first

- **16 of 505 deals can be shown; 486 are held; 3 are unsettled.** A deal is shown when at least one of its evidence rows comes from a publisher whose verdict in `license_verdicts.csv` is "may be public"; held when every evidence row rests on a publisher who asks for permission; unsettled when none is public and at least one publisher's page has not been read.
- **Every shown deal rests on World Nuclear News** (the one outlet of the deals' feeds whose terms the ERW reads as public). The DOE newsroom carries one of them too (Vistra's loan), but through a story the evidence table has no row for (below). No shown row comes from a company's own announcement, a regulator's filing or an ISO's filing: the deals' feeds hold no such source today.
- **The shown subset is nuclear, and small in figures**: 3 of the 16 state MW (1,583 MW of the table's 37,221 MW stated by 27 rows) and 4 state dollars (USD 26.8 billion, of which USD 22.3 billion is Project Star and USD 4.2 billion Vistra's loan). Eleven are the same rows session 441 would count (public by every story); five more are shown here because this rule asks for one public evidence row rather than every story public.
- **Reuters and Bloomberg stand behind three in five of the held deals** (189 and 102 of 486); the ten publishers below cover 500 of the held rows' 523 evidence rows.
- **What a ruling would change, not code**: whether a deal's figures, extracted by the model from every story of its cluster, may be shown when a public outlet reports the deal and a held outlet reports it too (4 of the 16: Vistra, Constellation and Amazon, Project Star, the Netherlands' FEED studies); and whether Energy-Storage.news and Electrek are read, which settles the 3 unsettled rows. Both are in `deals-rulings-2026-10-23.md` (session 832).

## The rule and how it was read

- **The evidence rows.** `energy_deals_evidence` holds one row a deal and story where the model returned an evidence sentence: 557 rows for 505 deals (463 deals with one row, 34 with two, 6 with three, 2 with four). The deals' `story_ids` name 790 stories, so 233 stories have no evidence row; for the 16 shown deals the story-only publishers are listed below and none changes a sort (they add held outlets to three deals that are shown already).
- **From a source to a publisher.** The evidence row's `source` goes through `warehouse/metadata/sources.csv` (source to publisher) and `canon()` of `scripts/licenses.py`: "Bloomberg.com" is Bloomberg, "jpt.spe.org" and "JPT Homepage" are JPT, "hartenergy.com" is Hart Energy.
- **From a publisher to a verdict.** `warehouse/metadata/license_verdicts.csv`, the file `docs/licenses.md` is written from: "may be public" is public; "needs written permission" or "needs a paid license" asks; no row is "not read".
- **The three sorts.** Shown: any public evidence row. Unsettled: no public row, at least one publisher not read. Held: everything else (a deal with no evidence row would be held; today every deal has one).
- **Session 441's rule differs** (`sources-by-row-2026-10-21.md`): it asks every story of the deal to be public and found 9 of 492; on today's file it finds 11 of 505. The chain's rule for the tracker is the one above (a public source stands behind the deal, said as such on its row, the held outlets never named), and the difference between the two counts, 5 deals, is the first item for the owner's ruling below.

## The counts

| Sort | Deals | With MW | MW | With USD | USD |
|---|---|---|---|---|---|
| shown | 16 | 3 | 1,583 | 4 | 26,839,000,000 |
| held | 486 | 24 | 35,638 | the rest | the rest |
| unsettled | 3 | 0 | 0 | 0 | 0 |
| all | 505 | 27 | 37,221 | | |

## The shown rows and their public evidence

| Date | Deal | Type | Parties | Asset | MW | USD | Public evidence (publisher, story date) | Other publishers in the evidence rows |
|---|---|---|---|---|---|---|---|---|
| 2026-10-22 | deal:db1f505b8bd9ed04 | other | US Navy / Radiant | Kaleidos microreactor at Naval Weapons Station Crane |  |  | World Nuclear News (2026-10-22) | none |
| 2026-10-22 | deal:2eafe13b10e3f733 | joint_venture | SGE; Origin Nuclear; Ontario Power Generation | planned UK BWRX-300 fleet |  |  | World Nuclear News (2026-10-22) | none |
| 2026-10-19 | deal:d6eda0ffd6db76cd | smr | Amazon / AEP | 960 MW project at a former coal plant site in Sullivan County, Indiana | 960 |  | World Nuclear News (2026-10-19) | none (six story-only outlets, below) |
| 2026-10-19 | deal:b2f3d832a4fa0f52 | ppa | PT Pembangkit Listrik Nuklir / Rosatom | floating nuclear power plants |  |  | World Nuclear News (2026-10-19) | none |
| 2026-10-15 | deal:22af83288d1df241 | joint_venture | SGE / ZE Pak | nuclear power plant in Patnow (Pątnów) |  |  | World Nuclear News (2026-10-15) | none |
| 2026-10-14 | deal:6daa5127a8a81cab | other | Westinghouse / four Polish companies | safety-related modules for Poland's first nuclear power plant |  |  | World Nuclear News (2026-10-14) | none |
| 2026-10-13 | deal:12f09b2267a3d2ef | other | Poland's Ministry of Energy; Polskie Elektrownie Jądrowe; Polska Grupa Energetyczna | second Polish nuclear power plant |  |  | World Nuclear News (2026-10-13) | none |
| 2026-10-08 | deal:3e77f0878dee58f3 | other | Polskie Elektrownie Jądrowe / Westinghouse | long-lead items for the first unit of Poland's first nuclear power plant, three AP1000 reactors |  |  | World Nuclear News (2026-10-08) | none |
| 2026-10-08 | deal:2049dd8e3a5413cf | m_and_a | ČEZ | JESS |  | 211,000,000 | World Nuclear News (2026-10-08) | none |
| 2026-10-08 | deal:01b0163eef7a0337 | other | Westinghouse / Hyundai Engineering & Construction | FEED studies for two AP1000 nuclear plants in the Netherlands |  |  | World Nuclear News (2026-10-08) | ANS Nuclear Newswire |
| 2026-10-05 | deal:70bf30d372e1d674 | debt | Department of Energy / Vistra | Beaver Valley, Davis-Besse and Perry nuclear plants | 433 | 4,200,000,000 | World Nuclear News (2026-10-06) | POWER Magazine (and four story-only outlets, the DOE newsroom among them) |
| 2026-10-02 | deal:47c4c339a9ef5a9d | equity_raise | Polish business people / SGE | BWRX-300 small modular reactor projects |  | 128,000,000 | World Nuclear News (2026-10-02) | none |
| 2026-09-30 | deal:c2360f3ea399a2c9 | project_finance | The United States Department of Commerce and the Government of the Republic of Korea / Related Companies | Project Star |  | 22,300,000,000 | World Nuclear News (2026-10-01) | Financial Times, ANS Nuclear Newswire |
| 2026-09-30 | deal:6d416fb10be3a6f0 | ppa | Amazon / Constellation | Maryland nuclear plant | 190 |  | World Nuclear News (2026-10-01) | Reuters, Utility Dive (and three story-only outlets) |
| 2026-09-30 | deal:3c1f461ac1000983 | other | Sellafield | asset care framework at Sellafield site |  |  | World Nuclear News (2026-09-30) | none |
| 2026-09-29 | deal:ea783b38ea44bf8f | m_and_a | Dutch government | EPZ |  |  | World Nuclear News (2026-09-29) | none |

Story-only publishers (named in `story_ids`, no evidence row), for the record: Amazon and AEP's 960 MW (ANS Nuclear Newswire, Bloomberg, Data Center Dynamics, Financial Times, POWER Magazine, Utility Dive); Vistra's loan (ANS Nuclear Newswire, DOE newsroom, Rigzone, Utility Dive); Amazon and Constellation (ANS Nuclear Newswire, Data Center Dynamics, OilPrice.com). The 790 story ids were all found in `news_stories`.

## The ten publishers behind the held rows

| Publisher | Verdict | Held deals resting on it | Evidence rows |
|---|---|---|---|
| Reuters | needs written permission | 189 | 193 |
| Bloomberg | needs written permission | 102 | 105 |
| Hart Energy | needs written permission | 62 | 62 |
| Financial Times | needs written permission | 35 | 35 |
| WSJ | needs written permission | 35 | 35 |
| Rigzone | needs written permission | 25 | 25 |
| LNG Prime | needs written permission | 21 | 21 |
| Data Center Dynamics | needs written permission | 13 | 13 |
| JPT | needs written permission | 9 | 9 |
| OilPrice.com | needs written permission | 9 | 9 |

The rest of the held rows rest on ANS Nuclear Newswire, POWER Magazine, pv magazine USA, Natural Gas Intelligence, Data Center Frontier, Utility Dive, Canary Media, Heatmap News, Latitude Media and Data Center Knowledge, each with fewer than nine.

## The unsettled rows

| Deal | Date | Type | Parties | Asset | Publisher not read |
|---|---|---|---|---|---|
| deal:36ca228d7079e592 | 2026-10-06 | ppa | EDP / Zelestra | two hybrid solar-plus-storage PPAs | Energy-Storage.news |
| deal:1cba9c21aefdcb0c | 2026-09-28 | m_and_a | Geely Holding subsidiary / NIO | 30% of NIO Power | Electrek |
| deal:5453b24bfaa3651a | 2026-09-25 | m_and_a | ESR / Aquila Clean Energy APAC | Aquila Clean Energy APAC | Energy-Storage.news |

Neither publisher's terms page has been read (`docs/licenses.md`, the publishers no read covers). Reading them is a request, which this chain does not make.

## Decisions made without you (session 821)

- The evidence table, not `story_ids`, is the rule's input, as the chain's words say; the story-only publishers are listed so that the owner sees what the rule leaves out (no sort changes).
- "A company's own announcement, a regulator's or an ISO's filing, a government page" are read through the verdicts file like any publisher (the DOE newsroom's row there is "may be public"); none of the three kinds appears in today's evidence rows.
- A deal with no evidence row would be held, not unsettled: nothing stands behind it that the rule can read. Today every deal has one.
- The reader lives in `warehouse/deals/public_rows.py` (a reader: no write under `warehouse/output`, no request), so that session 822 and the tests use the one sort.

## For Samuel's ruling

- Whether a figure of a shown deal may be drawn when the deal's cluster holds a held outlet's story too (the model read every story; a field cannot be traced to one): 4 of the 16 today. The chain's rule shows every column; the stricter rule (every story public, session 441's) shows 11 deals.
- Whether Energy-Storage.news and Electrek are read, which settles 3 deals.
