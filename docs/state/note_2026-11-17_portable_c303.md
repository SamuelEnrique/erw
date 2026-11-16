# The portable laptop, chain 303: the two trackers to the five tools' done line (16 November 2026)

Energy Research Warehouse (ERW), session 7407, for Samuel. Chain 303 (`queue/done/303-night-16-november-portable-trackers-done-line.md`), the portable laptop (code role), 16 November 2026, about 09:10 to 10:20 UTC, Fable at high effort, one Claude Code session. Sessions 7400 to 7407. The file's name carries the 17th because the chain's prompt names it so; the work ended on the 16th.

- **Model spend: USD 0.** `ERW_SPEND_CAP_USD=0`; no script that calls a model was run. No warehouse table written; `site/lib/release.ts` untouched; no hold lifted or worked around; nothing sent, posted or published; no LinkedIn, Digest or Roundup work.
- **No build on this laptop:** 1.7 to 1.9 GB free. The stack's changes are held by tests and a type check of the changed files (0 diagnostics); the landing gate's build is its first.
- **Both goals are done.** The optional third tool, `/companies`, was not taken: the data machine's branch `wip/c301-data` already holds `replication/companies`.
- **No next file**, and no machine's successor: the resume pointer is removed.

## Each tool against its done line

| Tool | Method note | Replication (today's rows) | Cross-check | Decisions block | Stata do-file | Waits |
|---|---|---|---|---|---|---|
| Datacenter tracker `/datacenters` | `docs/methods/datacenter_tracker.md`, complete, unsigned | 454 of 454 against the page's own functions | ten rows: Berkeley Lab, EIA, ERCOT, PJM, Dominion, AEP | on the page, twelve choices, default and source on hover | five lines, expected values at its top, not run (no Stata here) | your signature; five rulings; four rows for the data machine |
| Deal tracker `/deals` | `docs/methods/deal_tracker.md`, complete, unsigned | 1,123 of 1,124; the one difference named | six rows against CEBA, BloombergNEF, LevelTen; the twenty largest rows against their headlines (17 in a headline, 3 not checkable here) | on the page, thirteen choices, above session 465's list | six lines and a table by year and kind, not run | your signature; six rulings; four rows for the data machine; one open row that needs a build |

- **The signature pack:** `docs/reviews/trackers-signature-pack-2026-11-16.md`. Per tool: what you sign, the five choices that matter most, the cross-check in one table, the Stata commands and what each should print. One sitting, about forty minutes.

## What the work found

- **The datacenter tracker is a list of named sites, not a measure of megawatts.** 253 of its 274 counted facilities state no megawatts; five rows carry 25,000 of the 28,254 MW stated; "operator not stated" holds 26,124 of them. Against every published total it is small, for reasons the cross-check gives row by row.
- **Four of its megawatt rows are wrong against their own stories' words**: a tenant named as operator (1,000 MW), a fuel-cell plant's megawatts (702), a turbine project's (1,200), and the known Utah join (9,400).
- **The deal tracker's figures are its headlines' figures; its weakness is what a row is.** Pledges and plans are kept as deals, and funding rounds of AI companies are tagged AI power, among the 529 rows the stricter prompt has not read.
- **"A deal is energy's where its asset is energy" is written in no prompt and no rubric.** A second reading with the prompt as it stands would not take the funding rounds out.
- **One site fault fixed with a test** (the rollups' list of states lacked Puerto Rico). The page's arithmetic for both trackers' top blocks now lives in library files Node can run, unchanged.

## What needs the key (not run; costs summed)

- A second reading of the 529 older deals: USD 3.0 (their 814 stories) to USD 10.6 (every story checked).
- A second reading of four datacenter rows: under USD 1; the whole news table, USD 2.9.
- **Sum: about USD 4 for the two narrow readings, about USD 13.5 for both tables whole.**

## What waits for you (each with its default; the work stands on the default)

1. **The two signatures.** Default: unsigned. The pack.
2. **The two do-files in Stata.** Default: not run. The pack's commands; a log of each lets a session set your lines beside the mirror's.
3. **The public repository tracks the held tables' own files** (`warehouse/output/energy_deals.csv`, `datacenter_facilities.csv`, both evidence tables and three more; the `.gitignore` allowlist predates the hold). Default: nothing changed.
4. **Datacenter tracker, five rulings:** held whole (stays); the grids' public peak and capacity under the hold (hidden); the map's copy of the facilities (unchanged); a source on hover for every figure of the site (unchanged); the views by operator reading the developer (the operator alone).
5. **Deal tracker, six rulings:** held whole (stays); a floor of "Sure" on the table (none); grey text as hover tips (unchanged); the three views reading a grid a story names (the state alone); a folded pair carrying over a figure only the folded row states (no: 433 MW is in no sum); the energy-asset rule written into the prompt (not written).
6. **PJM's two figures in the datacenter cross-check**, against PJM's data license. Default: kept, as facts with links.

## What waits for the data machine

- **Landing row 33** of `docs/state/landing_request_portable.md`: `wip/7400-trackers`, with main merged. Nothing for a visitor (no page is live); the internal view gains the two decisions blocks.
- **Datacenter faults rows 16 and 18 to 21, deals faults rows 24 to 27** (new, each marked `data machine`): a queue position's status shown as a facility's; the four megawatt rows; the capital view's stale file (529 against 590 rows); the pledges and the two compute contracts in the AI view's dollar list; a step toward a power purchase kept as one.
- **Deals faults row 29** (open): the first tab lists both rows of a folded pair. It needs a build, because the value check reads the built page.

## For the other machines

- The five tests that fail on main at `e83dd0e06` are not this stack's: `tests/test_session1011.py` (the site's copy of `llms.txt` is behind the package's) and the Thesis Builder's Node tests of sessions 143, 148, 156 and 161.
- The rows of 11 and 13 November's stories were not in this laptop's copy of `news_stories`, so three of the twenty largest deal rows were not checked against a headline.
