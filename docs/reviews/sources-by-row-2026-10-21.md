# The datacenter and deals tables, row by row, by what their sources allow

Energy Research Warehouse (ERW), session 441, 21 October 2026 (the chain `queue/done/017-night-21-october-third.md`, on portable-laptop). No table and no page was changed; no request was made. Every figure below is the output of `runs/chain_oct21_third/s441/count.py` (kept in `runs/`, which git ignores; its output is `runs/chain_oct21_third/s441/figures.json`), read from the files as they stood on this machine at 07:16 UTC on 21 October. `tests/test_session441.py` counts the same figures again from the same files by its own code.

## Read these first

- **11 of 1,330 rows rest only on sources whose verdict is "may be public"**: 2 of 420 rows of `datacenter_facilities` (both from ERCOT's interconnection queue) and 9 of 492 rows of `energy_deals` (all from World Nuclear News). `datacenter_projects` (143 rows) and `datacenter_operator_sites` (275 rows) hold none. The 11 are listed in [`sources-by-row-2026-10-21-public-rows.csv`](sources-by-row-2026-10-21-public-rows.csv).
- **None of the 11 states a MW figure** in `capacity_mw` or `mw`. The two ERCOT rows carry a queue position's MW in `queue_mw`: 133.0 (`ercot_queue:25INR0688`, "Giga Texas Data Center") and 58.26 (`ercot_queue:28INR0499`, "Alpha Digital Campus Combined-cycle and Co-located Load").
- **Read as the verdicts stand, a split table would show almost nothing today.** The four tables hold 28,313.9 MW (facilities), 23,514.9 MW (projects), 4,799.0 MW (operator sites) and 31,101.0 MW (deals) in their MW columns; the public subset holds 0 MW of it.
- **What would change the count is a ruling, not code.** The chain's prompt names "a company's own announcement page" as a public kind of source. The nine operators' location pages that `datacenter_operator_sites` reads are each company's own page, but `docs/licenses.md` gives every one of the nine the verdict "needs written permission". Were they ruled public, 275 of 275 operator sites (15 rows with MW, 4,799.0 MW) and 276 of 420 facilities would rest only on public sources (variant B below). That is for Samuel's ruling; this review does not make it.
- **The hold's list of publishers and the rows' own publishers differ.** `energy_deals` rests on Data Center Knowledge and Heatmap News (both "needs written permission") through a second or later story, and neither is in its row of `license_status.csv`; `datacenter_facilities` rests on OilPrice.com (the same) through its news members, also not named in its row. The hold is whole-table, so nothing shown changes, but the words beside "license needed" omit them.

## How a row's publishers were read

- **The publisher column.** Every row's `source` column, and for a row built from news stories, the `source` of every story named in its `story_ids` column, read from `news_stories.csv` (column `event_id` to column `source`). All 968 story ids of the two news tables were found there (196 in `datacenter_projects`, 772 in `energy_deals`, the sum of each table's `n_stories`); the evidence files (`datacenter_projects_evidence`, `energy_deals_evidence`) were the fallback and were never needed. A row of `datacenter_facilities` takes every publisher of every member named in its `member_ids` column: a `datacenter:` member that row of `datacenter_projects` (with all its stories), a `dcsite:` member that row of `datacenter_operator_sites`, an `ercot_queue:` member ERCOT, an `nyiso_queue:` member NYISO.
- **From a source's name to a publisher.** The name goes through `warehouse/metadata/sources.csv` (column `source` to column `publisher`) and then through `canon()` of `scripts/licenses.py`, the function that writes `docs/licenses.md`, so "Bloomberg.com" is Bloomberg, "jpt.spe.org" and "JPT Homepage" are JPT, and "digitalrealty:data-centers" is Digital Realty.
- **From a publisher to a verdict.** Column `verdict` ("As the ERW is today") of `warehouse/metadata/license_verdicts.csv`, the file `docs/licenses.md` is written from. "may be public" counts as public or permissive; "needs written permission" (every other verdict met here) counts as asking permission. A publisher without a row there is "not in the record": `docs/licenses.md` says such a publisher "has no verdict" and its table is "not settled, never public by default".
- **A row's class.** Public: every publisher it rests on "may be public". Asks permission: at least one "needs written permission". Not settled: none asks permission, but at least one is not in the record.
- **MW.** `capacity_mw` for the three entity tables (equal to `mw` on every row of all three) and `mw` for `energy_deals`. A row without a figure counts as a row, not as 0 MW. The MW beside a publisher sums the rows resting on it, so a row with three publishers is counted under each.

## The four tables

All four are "license needed" from 2026-10-21 in `warehouse/metadata/license_status.csv`.

| Table | Rows | Rows with MW | MW | Public rows | Asks permission | Not settled | Publishers its rows rest on |
|---|---|---|---|---|---|---|---|
| `datacenter_facilities` | 420 | 51 | 28,313.9 | 2 (0 MW) | 418 (51 with MW, 28,313.9 MW) | 0 | 24: 23 ask permission, 1 public (ERCOT) |
| `datacenter_projects` | 143 | 36 | 23,514.9 | 0 | 143 (36 with MW, 23,514.9 MW) | 0 | 13: all ask permission |
| `datacenter_operator_sites` | 275 | 15 | 4,799.0 | 0 | 275 (15 with MW, 4,799.0 MW) | 0 | 9: all ask permission |
| `energy_deals` | 492 | 23 | 31,101.0 | 9 (0 MW) | 480 (23 with MW, 31,101.0 MW) | 3 (0 MW) | 24: 20 ask permission, 2 public (World Nuclear News, DOE newsroom), 2 not in the record (Energy-Storage.news, Electrek) |

The three "not settled" deals rest on Energy-Storage.news (2) and Electrek (1) alone; neither publisher's page has been read (`docs/licenses.md`, "Publishers no read of this sweep covers").

Three variants of the rule, for the ruling:

| Variant | `datacenter_facilities` public | `datacenter_projects` | `datacenter_operator_sites` | `energy_deals` |
|---|---|---|---|---|
| A, the verdicts as they stand (every story of a row) | 2 rows, 0 MW | 0 | 0 | 9 rows, 0 MW |
| B, the nine operators' own pages counted public | 276 rows (15 with MW, 4,799.0 MW) | 0 | 275 rows (15 with MW, 4,799.0 MW) | 9 rows, 0 MW |
| C, a row's own `source` column only, its other stories ignored | 2 rows, 0 MW | 0 | 0 | 11 rows (10 World Nuclear News, 1 DOE newsroom), 433.0 MW |

Variant C is shown only so that its cost is clear: the model that wrote a deals row read every story of its cluster, and a field cannot be traced to one story. The DOE newsroom row (`deal:70bf30d372e1d674`, Beaver Valley, Davis-Besse and Perry, 433 MW) was also carried by POWER Magazine, Utility Dive, World Nuclear News, Rigzone and ANS Nuclear Newswire; four of those five ask permission. This review uses variant A.

### By publisher

#### `datacenter_facilities`: the publishers its rows rest on

| Publisher | Verdict (`license_verdicts.csv`) | Rows resting on it | Of which it is the row's `source` | MW of those rows |
|---|---|---|---|---|
| Digital Realty | needs written permission | 74 | 74 | 0.0 |
| Data Center Dynamics | needs written permission | 73 | 67 | 17,690.9 |
| Equinix | needs written permission | 73 | 73 | 0.0 |
| Google | needs written permission | 52 | 52 | 0.0 |
| Reuters | needs written permission | 47 | 36 | 2,740.0 |
| Meta | needs written permission | 28 | 28 | 0.0 |
| Bloomberg | needs written permission | 26 | 15 | 0.0 |
| Microsoft | needs written permission | 19 | 19 | 0.0 |
| WSJ | needs written permission | 14 | 7 | 9,400.0 |
| Vantage Data Centers | needs written permission | 13 | 13 | 3,917.0 |
| Amazon Web Services | needs written permission | 7 | 7 | 0.0 |
| Financial Times | needs written permission | 6 | 1 | 0.0 |
| Hart Energy | needs written permission | 5 | 4 | 3,000.0 |
| Switch | needs written permission | 5 | 5 | 882.0 |
| Data Center Knowledge | needs written permission | 4 | 3 | 73.0 |
| Oracle | needs written permission | 4 | 4 | 0.0 |
| Heatmap News | needs written permission | 3 | 3 | 0.0 |
| Data Center Frontier | needs written permission | 2 | 2 | 84.0 |
| ERCOT | may be public | 2 | 2 | 0.0 |
| Latitude Media | needs written permission | 1 | 1 | 0.0 |
| NYISO | needs written permission | 1 | 1 | 0.0 |
| Natural Gas Intelligence | needs written permission | 1 | 1 | 0.0 |
| OilPrice.com | needs written permission | 1 | 1 | 0.0 |
| POWER Magazine | needs written permission | 1 | 1 | 0.0 |

The one NYISO row (`nyiso_queue:1630`) is a queue position; NYISO's verdict is "needs written permission", so it is not in the public subset. Its row of `license_status.csv` names ISO-NE and MISO as well (the queues the builder reads, per its header's "Derived from"); no row rests on either today.

#### `datacenter_projects`: the publishers its rows rest on

| Publisher | Verdict (`license_verdicts.csv`) | Rows resting on it | Of which it is the row's `source` | MW of those rows |
|---|---|---|---|---|
| Data Center Dynamics | needs written permission | 73 | 67 | 17,690.9 |
| Reuters | needs written permission | 47 | 37 | 2,740.0 |
| Bloomberg | needs written permission | 26 | 15 | 0.0 |
| WSJ | needs written permission | 14 | 7 | 9,400.0 |
| Financial Times | needs written permission | 6 | 1 | 0.0 |
| Hart Energy | needs written permission | 5 | 4 | 3,000.0 |
| Data Center Knowledge | needs written permission | 4 | 3 | 73.0 |
| Heatmap News | needs written permission | 3 | 3 | 0.0 |
| Data Center Frontier | needs written permission | 2 | 2 | 84.0 |
| Latitude Media | needs written permission | 1 | 1 | 0.0 |
| Natural Gas Intelligence | needs written permission | 1 | 1 | 0.0 |
| OilPrice.com | needs written permission | 1 | 1 | 0.0 |
| POWER Magazine | needs written permission | 1 | 1 | 0.0 |

Reuters is the `source` of 37 projects and of 36 facilities: one Reuters project was merged into a Meta operator site (`kinds` "operator;news"), whose `source` is Meta's.

#### `datacenter_operator_sites`: the publishers its rows rest on

| Publisher | Verdict (`license_verdicts.csv`) | Rows resting on it | Of which it is the row's `source` | MW of those rows |
|---|---|---|---|---|
| Digital Realty | needs written permission | 74 | 74 | 0.0 |
| Equinix | needs written permission | 73 | 73 | 0.0 |
| Google | needs written permission | 52 | 52 | 0.0 |
| Meta | needs written permission | 28 | 28 | 0.0 |
| Microsoft | needs written permission | 19 | 19 | 0.0 |
| Vantage Data Centers | needs written permission | 13 | 13 | 3,917.0 |
| Amazon Web Services | needs written permission | 7 | 7 | 0.0 |
| Switch | needs written permission | 5 | 5 | 882.0 |
| Oracle | needs written permission | 4 | 4 | 0.0 |

Of the nine, Digital Realty, Equinix and Switch were not read (`docs/licenses.md`: "NOT READ", "Permission by default"). For Google the record's note reads "The terms say nothing against restating a fact a page gives." These are the facts a ruling on variant B would weigh.

#### `energy_deals`: the publishers its rows rest on

| Publisher | Verdict (`license_verdicts.csv`) | Rows resting on it | Of which it is the row's `source` | MW of those rows |
|---|---|---|---|---|
| Reuters | needs written permission | 221 | 176 | 11,822.0 |
| Bloomberg | needs written permission | 146 | 112 | 13,212.0 |
| Hart Energy | needs written permission | 81 | 56 | 7,052.0 |
| WSJ | needs written permission | 61 | 34 | 0.0 |
| Financial Times | needs written permission | 58 | 33 | 6,360.0 |
| Rigzone | needs written permission | 29 | 13 | 2,763.0 |
| LNG Prime | needs written permission | 22 | 19 | 720.0 |
| World Nuclear News | may be public | 16 | 10 | 5,183.0 |
| Data Center Dynamics | needs written permission | 15 | 8 | 5,714.0 |
| JPT | needs written permission | 11 | 8 | 0.0 |
| OilPrice.com | needs written permission | 11 | 6 | 190.0 |
| ANS Nuclear Newswire | needs written permission | 10 | 3 | 5,183.0 |
| Natural Gas Intelligence | needs written permission | 8 | 1 | 1,200.0 |
| POWER Magazine | needs written permission | 7 | 2 | 10,528.0 |
| Utility Dive | needs written permission | 5 | 1 | 5,183.0 |
| pv magazine USA | needs written permission | 4 | 3 | 509.0 |
| Heatmap News | needs written permission | 3 | 0 | 5,700.0 |
| Data Center Frontier | needs written permission | 2 | 2 | 0.0 |
| Energy-Storage.news | not in the record | 2 | 2 | 0.0 |
| Canary Media | needs written permission | 1 | 0 | 3,600.0 |
| DOE newsroom | may be public | 1 | 1 | 433.0 |
| Data Center Knowledge | needs written permission | 1 | 0 | 0.0 |
| Electrek | not in the record | 1 | 1 | 0.0 |
| Latitude Media | needs written permission | 1 | 1 | 0.0 |

World Nuclear News is under 16 deals and holds 5,183.0 MW of them, but 7 of the 16 were also carried by a publisher that asks permission, and those 7 hold all 5,183.0 MW; the 9 it carries alone state no MW. Its licence is itself narrow: "You may reproduce sections of up to 150 words from individual pages [...] Any reproduced sections must carry attribution to the World Nuclear Association" (`license_verdicts.csv`, its sentence). A deals row holds the model's fields and the story's link, no outlet text (`HOLDS` in `scripts/licenses.py`), so a page showing the 9 would cite World Nuclear News and link the story.

## The subset a page could show today

The 11 rows of variant A, in full in [`sources-by-row-2026-10-21-public-rows.csv`](sources-by-row-2026-10-21-public-rows.csv) (columns: table, id, name, state, mw, queue_mw, publishers, source, source_url):

| Table | Id | Name (the row's `name`, or `asset` for a deal) | MW |
|---|---|---|---|
| `datacenter_facilities` | `datacenter:ercot_queue-25INR0688` | Giga Texas Data Center (TX) | queue 133.0 |
| `datacenter_facilities` | `datacenter:ercot_queue-28INR0499` | Alpha Digital Campus Combined-cycle and Co-located Load (TX) | queue 58.26 |
| `energy_deals` | `deal:12f09b2267a3d2ef` | second Polish nuclear power plant | none |
| `energy_deals` | `deal:2049dd8e3a5413cf` | JESS | none |
| `energy_deals` | `deal:22af83288d1df241` | nuclear power plant in Pątnów | none |
| `energy_deals` | `deal:3c1f461ac1000983` | asset care framework at Sellafield site | none |
| `energy_deals` | `deal:3e77f0878dee58f3` | long-lead items for the first unit of Poland's first nuclear power plant, three AP1000 reactors | none |
| `energy_deals` | `deal:47c4c339a9ef5a9d` | BWRX-300 small modular reactor projects | none |
| `energy_deals` | `deal:6daa5127a8a81cab` | safety-related modules for Poland's first nuclear power plant | none |
| `energy_deals` | `deal:b2f3d832a4fa0f52` | floating nuclear power plants | none |
| `energy_deals` | `deal:ea783b38ea44bf8f` | EPZ | none |

The reading: `state` is empty on all 9 deals, and their story addresses name places outside the United States (Poland, Slovakia, Sellafield, Indonesia, Borssele); none of the 11 is a figure a page leads with. A split table is worth building for when a ruling or a permission frees a publisher (variant B, or a letter answered), not for these rows.

## The split table: the method for the code machine

The site already holds one table row by row: a table whose deciding publishers are all grid operators is held for those grids' rows only (`licenseByGrid` in `site/lib/license.ts`, session 207). The method below gives the four tables the same shape, keyed on each row's own publishers instead of a grid prefix. It changes no figure until a publisher is freed, because today's public rows are the 11 above.

1. **The rows carry their publishers.** Each builder (`warehouse/derived/datacenter_facilities.py`, and the writers of `datacenter_projects`, `datacenter_operator_sites` and `energy_deals`) writes two columns: `publishers`, the canonical names of every publisher the row rests on, sorted and joined with "; ", read exactly as this review read them (the row's `source`, every story of `story_ids` through `news_stories`, every member of `member_ids`); and `license`, one of `public`, `license needed` or `unsettled`, by the class rule above. One function computes both, in `warehouse/metadata/license_status.py` (the one reader of the license files for the builders), from `sources.csv`, `scripts/licenses.py`'s `canon()`, `license_verdicts.csv` and the `permission` column of `license_status.csv`: a publisher with a recorded permission counts as public for that table.
2. **The license is recomputed at every load.** A verdict or a permission changes without a data pull, so `warehouse/supabase/load.py` recomputes `license` from `publishers` before it writes a by-row table, and the validator fails a file whose `license` disagrees with its `publishers`. A story that cannot be found makes its row `unsettled`, never `public`.
3. **The status file names the mode.** `license_status.csv` gains a column `hold` (`table`, the default, or `row`); `scripts/licenses.py status` copies it into `site/data/license_status.json`. `site/lib/license.ts` gains `licenseByRow(table)`.
4. **The reads filter.** In `site/lib/supabase.ts` a read of a by-row table that is held adds `license=eq.public` and does not throw `LicenseNeeded`; the count of held rows is read once, so a page can say "N rows held for a license" beside what it shows. `components/Num.tsx` draws the catalogue's words for a check key that names a held row. `/api/download` serves the public rows of a by-row table, with a header line naming how many were held and why; `/data`'s catalogue lists the table as "public in part".
5. **Redivis follows the site.** `release_v1.py` puts only the public rows of a by-row table in the release and says so in the table's description.

### The tests it needs

- **The class rule** (Python, beside `tests/test_session207*`): a row resting only on ERCOT is `public`; ERCOT and Reuters `license needed`; Electrek alone `unsettled`; a facility merging an operator site and a news story takes the strictest of its members; a story id missing from `news_stories` makes the row `unsettled`; a permission recorded for Reuters in `license_status.csv` makes the ERCOT and Reuters row `public` for that table only.
- **The recount**: on the files of 20 October, `public` rows are 2 (facilities), 0, 0 and 9 (deals), the counts of this review; `tests/test_session441.py` holds the recount the builder's numbers should equal.
- **The guard**: the validator refuses a by-row table whose `license` column disagrees with its `publishers`, and one whose `publishers` names a publisher absent from `license_verdicts.csv` without the row being `unsettled`.
- **The status file**: `licenses.py status` writes `hold` into the JSON; `licenseByGrid` and `licenseByRow` are never both true for one table.
- **The site** (Node, as the `check-*.mjs` scripts): a held by-row read sends `license=eq.public`; a `Num` whose key names a held row draws "license needed"; `/api/download` on `energy_deals` returns 9 rows and the held line; the built HTML of `/datacenters` and `/deals` contains no id or name of a held row (grep the build for every held row's id); `check-table-downloads` counts a by-row table as offered in part.
- **The release**: `release_v1.py --check` fails when a by-row table's release holds a row whose `license` is not `public`.

None of this is built here: no file under `site/`, no builder and no table was changed.
