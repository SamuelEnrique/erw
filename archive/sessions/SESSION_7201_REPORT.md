# Session 7201 report: the large-load rules on the site (chain 302, goal 1)

Energy Research Warehouse (ERW). 16 November 2026, samueloldlaptop (code role), unattended. Chain file: `queue/done/302-day-16-november-oldlaptop-large-load-on-the-site.md`. Branch `wip/7200-large-load` (worktree `erw-7200`), landing request row 15. Model spend: USD 0.00, no model call. Session 7200 was interrupted eight minutes after its first commit and wrote no report: this report covers both.

## At the top

- **Not built and not seen in a browser on this machine.** A site build needs 2.5 GB of memory free (the chain's rule 6); the most free today was 2.0 GB. So no screenshot at 1280 or 390 exists, the hover and A and B were not exercised in a browser, and axe was not run. What stands in for it is below ("Drawn without a build"). The desk's landing gate builds the site; the browser steps are listed under "To finish".
- **One fault on main that is not this branch's:** `tests/test_session705.py` fails on clean `origin/main` on this machine (`connect.json` against its table: `lbnl_interconnection_queue` where the file says `interconnection_durations`).

## What a reader can now do

- **Open a utility's rule from the tab.** Each row's Utility cell and Time to connect cell draw one more line. Of the 48 hub and zone rows: 21 open a utility's own rule, 10 open the state's rule alone (the Texas hubs: the PUCT's 16 TAC 25.194), 6 say "no large-load rule found" (the research note's own line on hover), 11 say "no large-load rule read" with the count of rules read in the state as a link.
- **Read a rule in full:** status and date, docket, the eight fields as the document prints them, each with its cite on hover, the document linked, the ERW's notes.
- **Compare two rules** as A and B, each field whole.
- **Filter and sort 122 rules** by state, grid, status and name; the filters, the sort, A and B and the open rule are in the address.
- **See what changed in 90 days:** 94 changes, newest first, by region, each with its document and a button to the rule it changed.
- **Reach the state's law** on `/policy?view=monitor`, from a rule's state.
- **Download** the rows shown (CSV, Python, Stata), made in the browser.

## What was built

- `warehouse/derived/large_load_rules_page.py` writes `site/data/siting/large_load_rules.json` from the three tables (session 7200); its rules in a fixed order (7201).
- `site/lib/largeloadrules.ts`: pure, no import; what is shown and in what order.
- `site/components/largeload/`: the tip, the blank cell, a rule in full, the download made on the click.
- `site/app/cost-of-power/LargeLoadSection.tsx` and `LargeLoadRules.tsx`; `AllGridsView.tsx` draws the two cells' lines and the section.
- `site/app/policy/StateLaws.tsx`, in `MonitorView.tsx` under the records, following the State filter.
- `site/scripts/tsx-loader.mjs`: a Node hook that draws the site's components to HTML without a build.
- Method notes: `docs/methods/siting.md` (version 13), `docs/methods/large_load_research.md` ("On the site").

## Held to the tables by tests

- **The page file** (`tests/test_session7200_large_load_rules_page.py`, 7): the committed file equals the build from the committed research files; every value and cite is its table row's; the counts by status are the tables'; no value of a held row and no withheld field is in the file.
- **The library** (`site/scripts/test-large-load-rules.mjs`, 83 checks): filters, sorts, a row's rules, the changes, the laws, the CSVs.
- **Drawn without a build** (`site/scripts/test-large-load-render.mjs`, 52 checks):
  - every component draws; every tip has its one target; every button has a name;
  - **228 blank cells** say "license needed" in the rules table (220 of the 22 held rows, 8 fields of public rows), 16 in the changes, 4 in the laws;
  - 251 values and cites of held rows searched for in the drawn pages: none found;
  - every count the pages print is the file's (`largeload|...` check keys, also in `check-values.mjs`);
  - the section adds 163 thousand characters to the tab as it opens.
- **The wiring** (`tests/test_session7201_large_load_on_site.py`, 16).
- **The touched test files:** 189 files that name a changed module, each in its own process, 2,160 tests. 186 passed as they were; 2 older pins were moved with their reasons (`test_session215`: the check prefix `largeload`; `test_session332`: the monitor's downloads line now names `state_large_load_laws`); 1 fails on main too (above).
- Type check clean for the new files; lint clean.

## What to review (after the landing; both pages are in review)

1. `https://erw-flame.vercel.app/cost-of-power?view=allgrids`
   - Row "ERCOT LZ_AEN", column Utility: the last line reads "3 large-load rules". Click it. The page moves to "The large-load rule at ERCOT LZ_AEN": Austin Energy's rule, Oncor's, then the PUCT's rule under "Binding every utility of TX in ERCOT", then "Pedernales Electric Coop, Inc: no large-load rule found".
   - Hover "source" beside any field: the page or section and the document's words.
   - Scroll to "Large-load rules by utility". The line reads "122 rules ...: 52 in effect, 21 approved, 25 proposed, 1 ordered, 1 denied, and 22 held".
   - State: choose VA. 8 rules. Click A on Dominion's Rate Schedule GS-5 and B on NOVEC's Schedule HV-1: "Two rules, side by side" appears above the filters.
   - Status: choose "license needed (22)". Each row is a utility, its state and grid, and ten blank cells. Hover one: "license needed: ...".
   - "What changed in the last 90 days": 94. Click "South (29)". In the last column click a rule's name: the table above opens that rule.
   - "CSV of these", "Python", "Stata": three files.
2. `https://erw-flame.vercel.app/policy?view=monitor&state=MD#large-load-laws`
   - "State laws on large loads": 2 of 28 shown (Maryland's two). Click "every state": 28 rows; Indiana's row is its bill and four blank cells.
   - Hover a topic under "Requires" (for example "cost allocation"): the law's words and its section.

## Needs the key

- **Whether `/ask` answers from the three tables.** Not asked (rule 1). Known from the record: the site's chat reads the live set, the three tables are not in it, and on 15 November it refused all 58 questions written for them, rightly, by the table's name (`archive/sessions/SESSION_6130_6159_REPORT.md`). Asking the 58 again: about USD 4.80 (58 at about USD 0.082 a question, as sessions 6136, 6140 and 6141 measured).

## Decisions made without you

- **No database read on the tab.** The shared downloads line (`TableDownloads`) reads the catalogue from Supabase; the tab reads files only and keeps that. Its downloads are the rows shown, made in the browser. The monitor's downloads line (which already reads the catalogue) now names `state_large_load_laws`.
- **The page file reaches the browser inside one script, not in the HTML.** As props it would add about 940 thousand characters to every load of the tab.
- **Downloads are made on the click.** Drawn as links that hold the file, the CSVs put about a megabyte into the tab's HTML; the render test found it.
- **The table opens on 12 rules**, with "Next 12". Each row carries its eight hovers; 12 keeps the section at 163 thousand characters.
- **A field sorts by its words.** The fields are phrases ("25 MW and a load factor of 75 percent"), not numbers; the page says "A to Z" and draws no difference between A and B.
- **A held row's status is not printed.** The status filter has a choice "license needed (22)" for them.
- **Evergy Kansas South is not matched to Evergy's Kansas rule.** The rule's row names "Evergy Kansas Central, Inc. and Evergy Metro, Inc."; the SPP North hub's county utility is Evergy Kansas South (Kansas Gas and Electric). No guess: the row says "no large-load rule read, 3 in KS".
- **Two test pins moved**, each with its reason in the test.

## For Samuel's ruling

- **The three tables and the live set.** Their license verdict is unsettled (many hosts), so they are out of release v1, as the two registry tables are. Default taken: they stay out of the live set; the pages draw the public rows from the site file. If you rule them in, `/data` and `/api/download` offer the whole tables (`docs/state/data_requests_large_load.md`, row 18).
- **Evergy Kansas South and the Kansas LLPS rule** (above). Default: not matched. If the Kansas docket's applicants include Evergy Kansas South, one line in the builder's `RULE_EIA` joins them.
- **The blank cell.** Your page rule says a held value is drawn blank with "license needed" on hover; the tab's older cells print the words "license needed" in place. The new section follows the rule (blank, the words on hover and to a screen reader). Default: left as two forms; say if the older cells should go blank too.

## To finish (the desk, or this machine with 2.5 GB free)

- Build, then `node scripts/check-values.mjs` for `/cost-of-power?view=allgrids&llrow=ercot%3ALZ_AEN` and `/policy?view=monitor&state=MD`.
- `node scripts/check-390.mjs` and `node scripts/a11y-axe.mjs` on the same two pages; screenshots at 1280 and 390 into `docs/reviews/large-load-on-site/`.
- In a browser: hover a cell, set A and B, change a filter, open a rule from a change.
