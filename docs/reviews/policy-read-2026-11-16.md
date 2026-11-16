# The policy monitor read as a regulator's staffer would read it (chain 302, session 7204, 16 November 2026)

Energy Research Warehouse (ERW). The monitor view of `/policy` (`/policy?view=monitor`), with the states' laws on large loads that chain 302 put under its records, read for ten states as the staffer of a utility commission would: what is in motion for my state, what does my state's law require, what are the utilities filing. First the five states of the All grids tab's read (Texas, Virginia, Arizona, Ohio, Georgia), then the next five by the megawatts the datacenter tracker holds (`datacenter_facilities` on this machine: Utah, Alaska, West Virginia, Kentucky, Michigan; Ohio and Georgia lead that list and are among the first five).

**How it was read.** No site build on this machine on the day (memory). The monitor was drawn to HTML with its own component and file (`site/scripts/tsx-loader.mjs`) for each state, at the view's opening significance and at every significance, and its text and hovers read. No click was made.

## What each state shows

| State | Records at significance 5 or more (all) | Its law in the table | The utilities' rules read |
|---|---|---|---|
| Texas | 45 (101): FERC 41, the PUCT 20, the Governor 17 | S.B. 6: read and not shown (row 5) | 11, with 13 changes in 90 days |
| Virginia | 7 (27), all federal | 1: enacted (Code of Virginia 56-596.7) | 8 |
| Arizona | 4 (16), all federal | none found where searched | 3 |
| Ohio | 4 (22), all federal | 1: passed one chamber (Sub. H.B. 646) | 4 |
| Georgia | 4 (14), all federal | not read | 1 |
| Utah | 3 | 1: in effect (S.B. 132, 100 MW) | 1 |
| Alaska | 16 | not searched | none |
| West Virginia | 3 | 1: in effect (H.B. 2014) | 1, held |
| Kentucky | 8 | not read | 4 |
| Michigan | 3 | 1: in effect (a sales tax exemption) | 6 |

## The rows

Kind: `site` (fixed here, with a test), `data machine` (a row of `docs/state/data_requests_large_load.md`), `ruling` (written with the default taken).

| # | States | The place | What the reader meets | Kind | State |
|---:|---|---|---|---|---|
| 1 | Texas, Arizona, Georgia, Alaska, Kentucky | "State laws on large loads", a state with no row | "No law or bill on large loads was read for TX". Wrong in three ways: Texas's S.B. 6 was read and is withheld; Georgia's and Kentucky's legislatures' sites were not read; Arizona was searched and nothing found by subject; Alaska was not searched | site | fixed: each says what the research records ("S.B. 6, read and not shown", "not read", "none found where searched", "not searched"), with what was searched on hover. A lead from the news is not carried: there the hover names the research file |
| 2 | all | the same line | "28 are held for other states": "held" is the site's word for a license hold | site | fixed: "The table has 28 rows for other states" |
| 3 | all | under a state's law | The staffer who finds the law finds nothing of the utilities' own rules or of what changed in 90 days: they are on another page, unlinked | site | fixed: a chosen state links its utilities' rules on the All grids tab with their count and the changes'; there the State filter now chooses the changes too |
| 4 | all | the State filter | Virginia opens on 7 records, all federal. The hover said "A state the record's documents apply to." It did not say that a record is a federal action or a release, and that a state commission's own dockets are not records | site | fixed: the hover says what a record is, and that a grid operator's action naming no state is under Grid |
| 5 | Texas | Texas's row | S.B. 6 is the law the Commission's large-load rule carries out, and its cells are blank: the copy the ERW read sits on a path the legislature's robots file disallows | data machine | requested (row 26): an allowed official copy |
| 6 | Georgia, Kentucky, California, New Hampshire, Oklahoma, Tennessee; Alaska, Hawaii | no row | Six legislatures' sites could not be read (built by script, a robots file, a 404), and two states were not searched: none is ruled out | data machine | requested (row 27) |
| 7 | all | the records | 6 of the 1,522 records name large loads or data centers. FERC's order on PJM's large-load tariff (9 October 2026) is no record: FERC's orders in tariff dockets are not in the Federal Register, the monitor's source. The 15 grid operators' and FERC's changes of the large-load table hold them, on the other page | data machine | requested (row 28) |
| 8 | Virginia, Ohio | the State filter | 16 records name PJM; 7 of them name a state. A staffer who filters by Virginia does not see the 9 PJM-wide actions that bind Virginia | ruling | default: left; the Grid filter stands beside the State filter, and row 4's hover now says so |
| 9 | Virginia | "Requires" | "curtailment or backup generation" drawn twice: two requirements under one topic read as one word repeated | site | fixed: numbered in place ("1 of 2", "2 of 2") |
| 10 | Alabama, Utah, West Virginia; Texas | a law's bill, title or requirement; a rule's minimum bill | The research's working words reach the page in six cells: "as window A's registry names it" (Alabama's bill), "steps and clocks held in window A's registry" (Utah), "per the brief's lead" (West Virginia), "window A" in two Texas rules' minimum bill and one change; and in 45 notes (hovers) | data machine | requested (row 29): the page prints the tables' words as written, so the words are corrected in the research files |
| 11 | Michigan | Michigan's row | The one Michigan law in the table is a sales tax exemption for enterprise data centers, with no smallest load: it is a law on data centers, not on a large load's connection | ruling | default: left as the table has it (the research's scope was laws that set terms for large loads or data centers) |

## What a regulator's staffer still cannot get from the monitor, and why

- **Their own commission's dockets.** The monitor's records are the Federal Register's and four bodies' releases. The commissions' large-load proceedings the ERW reads are in the week view and on "What a datacenter pays", and several commissions are not read at all (Virginia's is paused for its robots file; Ohio's and Illinois's answer with a check for robots).
- **FERC's orders on the grid operators' large-load tariffs,** as records with their next steps (row 7).
- **The law of the state with the most at stake.** Texas S.B. 6 is named and blank (row 5).
- **A law's history.** One row a bill, at its status on the day it was read (13 or 14 November 2026); nothing re-reads it on a clock.
