# Session 1436 report: the first dry run of the Roundup, read as a reader, the preview sent

Energy Research Warehouse (ERW), session 1436 (chain 149's "1433"), `queue/done/149-day-5-november-code-periodicals-excellent.md`, samueloldlaptop, 6 November 2026, about 01:29 to 01:40 UTC. Model Fable 5.1, high effort. **Model spend USD 0.0277** (W44: headlines USD 0.0075, summary USD 0.0046; W43: USD 0.0113 and 0.0043; cap USD 4; the ledger off as session 2705 ran it, the costs from the run logs). No warehouse data written; one preview email to the fixed recipient; web requests to the Claude API (four calls), the ERW's own database (reads) and Resend (one send).

## What is in your inbox

- 01:33 UTC, **"[preview, dry run 1436] ERW Weekly | Gingerah Energy refers 1,000 MW data centre complex with 5GWh battery in Western Australia to EPBC Act; SPP SPPSOUTH_HUB day-ahead +37.1% on the week"** (Resend id `01a1ae7d-a394-7d8b-b07e-0eb79fdbcee8`), the v2 Roundup of W44 (26 October to 1 November) over the stories the stored issue used, to the one fixed recipient; never a subscriber; nothing claimed.

## What it did

- **The stored W44 issue** (`docs/roundup/2026-W44.md`, 1 November 23:28 UTC, the old code) read against the v2 shape: no masthead date, no opening number, no five numbers, no "What mattered", no next week, no fun fact; 67 scored stories (the scorer failed from 27 October); its numbers section says the week's day-ahead averages are "not in the warehouse (120 of 169 hours)", written before the week's hours were held (fault 40).
- **The dry runs** (`runs/periodicals_dryrun/s1436/run.sh`): W44 by the v2 code over the same 67 stories (`roundup/2026-W44.md`, 758 words as an email), and W43 (`roundup/2026-W43.md`, the newest fully scored week, 1,550 stories, 569 words) to read the five numbers and the chart over a full week; both rendered as emails (`email/`), W44 screenshotted at 390 and 1280 (`shots/`). W45 was not run: no story after 26 October 08:00 UTC is scored, and the chain's "W45 to date" would be empty.
- **The reading**: faults 25 to 40 appended to `docs/reviews/periodicals-faults-2026-11-05.md` (on `wip/1436-periodicals`), each with the line and the fix.

## What a sharp reader sees

1. **The opening number is a hub's weekly percentage move in both weeks** (SPP +37.1 percent, ERCOT -23.4 percent), which the rule forbids by default; no story names either hub, while Brent fell 6.4 percent and Henry Hub 12.9 percent on W44's week and W43's stories were 6,600 MW of reactors and a USD 45 billion deal (fault 25). The five numbers then print the same sentence again (26), two of the five are empty lines ("no deal ... is dated this week", 27), and the chart's number is the week before's with a file path in the body (28).
2. **An invented figure**: "the 1,000 MW is the outlet's figure" under a story about 1 GWh of storage (30); the same limitation sentence under every item (31).
3. **The chart of the week says three times that it is not the week's** (W44: WTI by rule, the stories point to crude exports; W43: CAISO Regulation Up, an ancillary price of the week before) (35).
4. The subject is a 160-character headline (34); next week's items are three FERC comment deadlines on one day with titles cut mid-word (36); "no scored story was published" when the scorer did not run (37).
5. What the v2 code does right over the old issue: the masthead, the missed-week line (W43 says W42 has no issue), every figure keyed, held prices without digits, the next-week section from the policy monitor's dates, the fun fact sourced, the fold.

## Checks

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 1436"` | 0 | on duty to 17:31 UTC |
| `roundup.py --week 2026-W44` and `--week 2026-W43` (the model, cap USD 4) | 0, 0 | USD 0.0121 and 0.0156 |
| `email_digest.render` (roundup) twice | | the character once in each |
| the two screenshots | 0 | `shots/email-W44-390.png`, `-1280.png` |
| `send_preview` (prefix "[preview, dry run 1436] ") | 0 | 1 of 1 fixed recipient, 01:33 UTC |
| em dashes in the files written | | none |

## Decisions made without you

- W44 and W43 instead of W45 (above); W43 not sent (its v2 preview is session 2705's, 25 October).
- The faults of the Roundup that are the Digest's (the why lines through `brief.why_line`) are listed once more with the Digest's number (32, 33) so the Roundup's session sees them, and are fixed by session 1437.
- The data machine's empty tables (deals, datacenters, the week's scored stories) are marked "data machine" in the rows they touch; the code's empty rows are the code's.

## For Samuel's ruling

- The Roundup's send hour (fault 40): the Sunday 23:00 UTC run writes the week's numbers before the week's hours are held; the brandbook's Friday 10:00 Eastern with a Thursday cutoff is in `docs/brand.md` section 10 with the workflow line. Not changed.
- A calendar table for "Next week" (what it would need: the policy monitor's comment deadlines and effective dates already give dated items; auctions, hearings and data releases need a source each: FERC's calendar, the ISOs' auction schedules, EIA's release schedule).
