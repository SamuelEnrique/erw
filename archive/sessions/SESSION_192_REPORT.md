# Session 192 report: Sunday's Roundup of 11 October takes "The peak hour moved"

11 October 2026, 07:14 to about 07:25 UTC (the work), unattended, on `lab-desktop`. Branch `wip/192-roundup-repeat` (`61bb398b` and this report), in `C:\Users\Shared\Documents\erw-192`, on this machine only. Model spend USD 0, no model call. No pull. Outputs: `runs/session192/` of the data checkout.

## Read these first

- **Landed since this was written**: merge `e5af1750` on `main`, 11 October 2026, 09:37 UTC, 0 differences on 25 pages, before the 23:00 UTC run. On main's code the dry run of 2026-W41 exits 0. See "Night of Oct 11" in `SESSION_185_REPORT.md`.
- **NOT LANDED, and it must land before 23:00 UTC today or the Roundup will most likely not be written.** This machine still cannot push to GitHub (no sign-in; session 184, item 0). The fix is one commit on a branch here. The commands are under "To finish".
- **The finding is marked.** "The peak hour moved" (ERCOT; card `peak_hour_moved`) is chosen for week 2026-W41, through the site's own "Use in Roundup" route at 07:16:08 UTC. `roundup_pick.py 2026-W41` reads it back.
- **The dry run found a fault that is not about the chart: this week's Roundup was not written at all.** `roundup.py --week 2026-W41 --no-model` stopped with "duplicate items in the brief". The Department of Energy's release of USD 4.2 billion for nuclear power is one of the week's stories and, as a policy action, a line under "Also this week"; the hard check refuses two items with one source address. It refuses them with the model too: the address is the same whatever the headline.
- **Fixed on the branch, as the daily digest was fixed in session 176.** The policy section drops the later line and names it in the log. With the fix the dry run writes the Roundup, and its "ERW's Chart of the Week" is the chosen card.
- **The cap is asked before a step, not during it.** On 10 October the daily run's news scoring alone spent USD 1.07 against the cap of USD 1.00, and every later model step was switched off. If Sunday's daily run does the same, the Roundup makes no model call. If the day stands under USD 1.00 at 23:00 UTC, the Roundup makes 3 calls, about USD 0.03. Detail below.

## What to review

- `runs/session192/roundup_W41_dry.md`: the Roundup as it would be written now, without the model (165 lines). Under "ERW's Chart of the Week": "**THE PEAK HOUR MOVED** (chosen for this Roundup)", the card's subtitle, its image, three callouts, its paragraph and its source line.
- `runs/session192/roundup_W41_dry_email.html`: the same as the email renders it. Nothing was sent. The image address answers 200 (198,225 bytes): `https://raw.githubusercontent.com/SamuelEnrique/erw/main/docs/analysis/findings/peak_hour_moved_1600x900.png`.
- `https://erw-flame.vercel.app/analysis/card/peak_hour_moved` (internal view): the card that was chosen. The button there is the one that was sent.
- Under "ERW's Policy of the Week" in the dry run: the NRC's Clinch River permit, then one line under "Also this week" (the Fermi America draft statement). The Department of Energy's line is not there twice.

## What was done

- **The choice.** `runs/session192/use_in_roundup.mjs`: opens the internal view, checks that the card's page holds the button, then sends what the button sends (`POST /api/analysis {kind: "roundup", card_id: "peak_hour_moved"}`). Answer: HTTP 200 `{"ok":true,"week":"2026-W41"}`. One row of `analysis_requests` was written by the site's function.
- **Which card.** `/analysis` lists "THE PEAK HOUR MOVED: FIVE GRIDS" (`peak_hour_grids`). The ERCOT card is the earlier single-grid one, kept at its own address, with its own button and a committed image. The prompt says ERCOT, so that one was chosen.
- **The fix.** `warehouse/news/roundup.py`: `policy_section` passes the policy lines through `brief.without_repeats` against everything above them; when every "Also this week" line was a repeat, the heading goes too. 17 lines added, 1 changed.
- **Tests.** `tests/test_session192.py`, 6 tests: the repeat is refused by the hard check with the publisher's title and with another headline; it is dropped and named; the heading goes with its last line; a section without a repeat is unchanged; `main` writes the section through it.

## The cap and Sunday's run

- The workflow asks `health.py budget` before each of its two model steps (`analysis_note`, then `roundup`). At or over the cap, each is run with `--no-model` and the Roundup still publishes.
- The cap on GitHub is USD 1.00: the runner's own rows of 10 October say "of USD 1.00 (DAILY_MODEL_USD)".
- **It is not a ceiling on the day.** A step that starts under the cap runs whole. From 5 to 10 October the news scoring alone cost USD 1.07 to 1.11 a day (16 calls). On Sunday 4 October it cost USD 0.90 (15 calls) and the shadow scoring after it USD 0.29: a Sunday like that one also passes USD 1.00 before the Roundup starts.
- What the two steps cost when they ran with the model (4 and 5 October): `analysis_note` 1 call, USD 0.006; `roundup` 2 calls, USD 0.022.
- So for Sunday 11 October:
  - Daily run spends USD 1.00 or more before 23:00 UTC (as on 10 October): the Roundup makes **0 model calls**.
  - Daily run ends under USD 1.00: the Roundup makes up to 3 calls, about USD 0.03, and the day can end that much over the cap.
- **One weakness, not fixed.** The Roundup's runner learns the day's spend from the ledger file it restores from the Redivis draft. Supabase's copy holds 0 ledger rows for 9 and 10 October, so it is no second source. If that restore fails, the budget reads USD 0.00 and both steps run with the model (about USD 0.03). The budget does not say "not read" in that case.
- Not read from here: the repository variable itself, and Sunday's daily run (it starts at 14:00 UTC).

## Checks run

| Check | Exit | Result |
|---|---|---|
| `use_in_roundup.mjs peak_hour_moved --check` (nothing sent) | 1, then 0 | first try looked for the button on `/analysis`, where this card is not listed; then on the card's own page |
| `use_in_roundup.mjs peak_hour_moved` | 0 | HTTP 200, week 2026-W41 |
| `roundup_pick.py 2026-W41` | 0 | "peak_hour_moved chosen for 2026-W41" |
| `roundup.py --week 2026-W41 --no-model --out ...`, main's code | 1 | "duplicate items in the brief" (`roundup_dry.out`) |
| the same, the branch's code over this machine's tables | 0 | written; "dropped a repeat of an item above" once (`roundup_dry_patched.out`) |
| `render_email.py` (no send) | 0 | the chart section and its image are in the email |
| `cap_check.py`, `cap_evidence.py` | 0, 0 | the figures above |
| `tests.test_session192` with 176, 170 and 119 | 0 | 103 tests, 3 skipped |

- **Not run:** the whole test suite; the site build (no site file changed).
- **Not verified:** a run with the model (spend USD 0). That the fix is enough with the model rests on the hard check's own code: it compares source addresses, which the model does not write.

## Pulls and spend

- Outside hosts: none but the project's own site, Supabase and one HEAD of the image on GitHub.
- Model spend: USD 0. The dry runs ran with `--no-model` and an empty key.
- Production: one row written (the choice). The dry runs wrote a log and a status file under `warehouse/output`, no table.

## Decisions made without you

- **The ERCOT card, not the five-grid card** (above). Reversible: click "Use in Roundup" on another card; the newest choice of the week wins.
- **The fault was fixed, not only reported.** The prompt asks to verify that the build takes the finding; it did not build. The change is the one session 176 made for the digest.
- **Only "Also this week" lines are dropped.** The week's first policy action is written as a paragraph, which the hard check does not read as an item. If it is also one of the five stories, it still appears twice. Not changed.

## To finish

After signing in to GitHub on this machine (a terminal, `git push`, then the sign-in window):

```bash
cd /c/Users/Shared/Documents/erw && git fetch origin
.venv/Scripts/python.exe scripts/freeze.py status; echo "exit=$?"
node site/scripts/snapshot-live.mjs take before192
git -C ../erw-192 push origin wip/192-roundup-repeat
git -C ../erw-192 push origin wip/192-roundup-repeat:task/192-roundup-repeat
# after the workflow's merge and the deploy:
node site/scripts/snapshot-live.mjs take after192
node site/scripts/snapshot-live.mjs compare before192 after192
```

- No site file changes, so the comparison should list 0 differences.
- If it cannot land before 23:00 UTC: run the workflow by hand after it lands (`roundup.yml`, `once` left at 0). The send guard refuses a second email for the week.

## The prompt

"Session 192 (long end 1:00): Sunday's Roundup of 11 October: mark the finding "The peak hour moved" (ERCOT) as this week's chart with "Use in Roundup", verify the Roundup build takes it in a dry run, and verify Sunday's scheduled run will not call a model beyond the daily cap." Unattended; the rules of CHAIN_OCT8_PROMPT.md; model spend USD 0, no model call; deploys allowed; this is the data machine.
