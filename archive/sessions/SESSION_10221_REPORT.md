# Session 10221 report: the AI energy page audited as a hostile expert would

Chain 710, part D, 26 November 2026, the old laptop, worktree `erw-c710-a`. One tool: `/ai-energy` ("Energy per AI query, as published"). The audit: `docs/reviews/ai-energy-model-audit-2026-11-26.md`, its evidence in `docs/reviews/ai-energy-model-audit-2026-11-26/`.

## What was done

- The arithmetic is right: 96 of 96 items of the default view restated from the page's file to the digit, against the page as the site's own code draws it.
- Eight findings: two Medium (a fleet's whole consumption shown as "the energy of AI"; one search, two publications, 87.5 to 1, never joined while the decisions say no two publications measure the same thing), six Low.
- Six words branches (1 to 5, 8), each with a test that fails on main, drawn and read (pass), merged as `wip/audit-ai-energy-words` (`a97ee059e`) for landing. Two test-only branches (6, 7) for ruling.
- No table written, no lock, no model call, no live service, no web read, no default changed. Model spend USD 0.

## Decisions made without you

- The six words branches conflict in `page.tsx`; the merge keeps every change (the lead from 3 with the hint from 2; both headline notes from 4 and 5).
- The tour's line (`site/lib/tour.ts`) is changed on branch 1: it is this tool's claim about itself, though drawn on the tour.
- The page's name is left as it is and put to you (below), since a tool's name is yours.
- No ratio of the ERW's own is put on the page for finding 2: the page's rule forbids it, so the words name the case and leave the two rows to the reader.
- The peer-review count's words say the rule rather than change the count: the venues of BLOOM's and the 2022 Patterson paper are an expert's knowledge, not verified here (data request 1).

## For Samuel's ruling (default "left as it is")

- Finding 6 (`wip/audit-ai-energy-6`, `643901d36`): show each figure with the digits printed. 2 of 23 figures change how they look (0.1 to 0.10 Wh; 0.0001 to 1.0x10-4 kWh); no value moves.
- Finding 7 (`wip/audit-ai-energy-7`, `5ad31bf5f`): group "What is measured" on the words before the parenthesis. 13 choices to 8; the fleet choice shows 5 rows, not 3; training 9, not 7.
- The page's name, "Energy per AI query": 7 of its 23 rows are per query, prompt or inference. Default: the name as it is.

## Needs the key

- Nothing.

## Returned to the chain's main session

- Landing row: `wip/audit-ai-energy-words` (`a97ee059e`), words only, figures unmoved.
- Three data requests (the saved copies on the data machine): the venues printed in two papers; the 2022 paper's ML share and its words on Strubell's estimate; the fleets' stated geography.
- For window B: the codebook's description of `ai_energy_published` says "per token"; no row is.
