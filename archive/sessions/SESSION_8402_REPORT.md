# Session 8402 report: the twelve figures that did not agree, each traced to its cause (chain 503, part A, step 3)

19 November 2026, samueloldlaptop (code role), unattended. On `main` (`86e038f0c`). Model spend USD 0. Nothing changed but the ranked list's own words and one request row: no page, no default, no branch, no table.

## What was done

- The section "Figures that do not agree" at the foot of `docs/reviews/rulings-ranked-2026-11-17.md` now gives, for each of its twelve entries, the right figure and one or two sentences on what was wrong, with both figures that disagreed kept.
- Ten were recomputed on this machine with scripts under `runs/c503/` (read-only); two could be traced but not fully recomputed (below).

## The causes

- **A rate of the wrong year (2):** entry 53 (the commission's 2025 transmission rate, 7.83, set beside 2026's 8.62 per MWh) and entry 117 (USD 20,564,190 at 2025's rate; right is USD 22,658,181).
- **A partial month (1):** entry 67 (this laptop's copy held 19 of October 2026's days; right is USD 80.34 per kW).
- **A rounding (3):** entry 48 (295,122 MWh, not 295,123), entry 89 (619,176 MWh; two programs land either side of a half) and entry 113 (+407.82 USD per MWh; the same).
- **A count taken two ways (2):** entry 78 (72 cells, six figures a month, not 48) and entry 119 (three shares on the view, so two would leave, not one).
- **A summary that miscounts its own printout (1):** entry 6 (7 Texas months fall to 0 MWh, not 8).
- **A file rebuilt between the two readings (1):** entry 18 (the EV game's price file of 17 November; right is USD 1,707 to 1,381 a year and USD 6,030 to 3,924 in present value).
- **Other (2):** entry 118 (both documents print "60 to 90 days"; the table holds the upper end in one row and no length in the other) and entry 127 (the measurement used solar's 35 years for a peaker's 30; right is the page's USD 2.38 million at the Houston hub).

## Corrected in the entries' own lines

- Entry 48's `Change` (+269,069 MWh on the table's values), entry 118's `Now`, `Other choice`, `Change` and one sentence of its recommendation, entry 119's three lines, entry 127's `Now`.

## One request to the data machine

- Row 320 of `docs/state/data_requests_done_line.md`: one rule for the two CAISO rows of `large_load_connection_rules` (the printed "60 to 90 days" held as 90 in one and as no length in the other). It meets ruling 1 of `docs/state/note_2026-11-13_data_c227.md`, which still waits.

## Not established

- Entry 119: which days the live set's daily table held on 16 November (it needs the live set; the 5.91 reproduces on this laptop's 43-day copy).
- Entry 127: the bar on the page as it opens for a peaker (the record's other bars imply about USD 48.1 per kW, where it would read about 2.66 million).
- Entry 53: the all-in figures were not recomputed and the commission's order of 5 November was not read.
- Entry 6: recomputed on this laptop's table of 4 October only.

## Needs the key

- Nothing.

## Decisions made without you

- Where a stored record holds its own margin (entry 48), that margin is taken as the right figure.
- One request row for the two CAISO rows, since one rule settles both.

## For Samuel's ruling

- Nothing new: entry 118's question is ruling 1 of the data machine's note of 13 November (the default: each row as written).
