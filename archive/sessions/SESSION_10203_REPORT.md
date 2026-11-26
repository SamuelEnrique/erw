# Session 10203 report: "What a datacenter pays" audited as a hostile expert would (chain 710, part B)

26 November 2026, the old laptop, worktree `erw-c710-b`. Model spend USD 0. No table written, no lock taken, no default moved, no site build, no browser.

## What was done

- `docs/reviews/datacenter-model-audit-2026-11-26.md`, with its scripts and printouts in `docs/reviews/datacenter-model-audit-2026-11-26/`.
- The arithmetic is right: an independent restatement from the method note gives the default page's figures to the digit (34.07 per MWh, USD 29,846,522 for 100 MW, bad month 37.88, 0.0691 per GPU-hour, 49,310 GPUs); 131 numbers equal the page's library to 1e-6; the replication passes 14 of 14.
- "If perfectly foreseen" is never below the rule's figure on 392 cases and 3,528 year rows.
- Eight findings: one High, three Medium, four Low. Eight branches `wip/audit-datacenter-1` to `-8`, each with its test, pushed.
- Words only, for landing: 1 (the scenarios' "all-in" GPU-hour renamed levelized and its note says what it holds), 2 (All grids' all-in names losses and what it leaves out), 3 (the load is a price taker, said), 5 (the contract is shaped like the load, said), 6 (the carbon is an average, not marginal, said). The five merge together cleanly onto origin/main; their tests and the page's tests pass together.
- Test only, not for landing: 4 (two kinds of dollars), 7 (GPU defaults), 8 (California at generator hubs).

## Decisions made without you

- The scenarios' row is renamed "Levelized power per GPU-hour" rather than only re-noted: "all-in" was the false word. The check key `a|allin` and the code's names are kept, so no check moves.
- Finding 2 is Low, not Medium: the All grids cell's hover already named delivery, distribution, ancillary and retail charges as left out; only losses and the column's tip were missing.
- Inflation of 2 and 2.5 percent is this audit's assumption, as in the battery and generator audits.
- The own-effect figures (finding 3) come from a rough one-curve merit order and are labelled so; they size the order of the effect only.
- The solar shape gap (finding 5) uses the generator page's public file (hub average, October 2025 to September 2026), the only hourly solar profile on this machine.
- Finding 5's note sentence was moved to the note's section 4.14 so that the words branches do not touch neighbouring lines.

## For Samuel's ruling

- Finding 4: flat prices at Lazard's money rate. Default "left as it is". With prices rising 2 percent a year the present value of 20 years for 100 MW is USD 299.42 million, not 261.19 (+14.6 percent); at 2.5 percent 310.24 (+18.8).
- Finding 7: the GPU defaults. Default "left as it is" (1.3 kW, 1.56). At the datasheet's 1.275 kW every GPU-hour is 1.9 percent lower; at an overhead ratio of 1.09 (the hover's Google fleet) 30.1 percent lower.

## Needs the key

- Nothing: no model call was needed or made.

## Problems

- `tests/test_session705.py` fails on origin/main as well (a data file against the machine's table); not this work's.
- `site/scripts/check-datacenter-scenarios.mjs` (its regex changed on branch 1) needs a built site and was not run.
- The pages were not drawn to HTML for the words branches; part D of the chain does that before a landing row is marked requested.
