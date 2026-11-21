# Sessions 9820 and 9821 report: the findings' charts drawn again (desktop window 4)

Energy Research Warehouse (ERW). 20 November 2026, lab-desktop, the fourth Claude Code window, unattended, from 20:08 UTC. Session numbers 9820 to 9839 checked free (no report, no commit, no queue file names them). Model spend USD 0.00: no model call. No warehouse table, no data lock, no daily run; the main folder's files read only. Every draft stays a draft: nothing approved, sent or posted; no caption; no LinkedIn work; chart titles untouched.

## At the top

- **Nothing unexpected in any snapshot.** Each push of images to main had a before and after snapshot of the 25 addresses; every comparison so far: "0 differences in all" (expected: images under `docs/findings/` and two documents change no page a visitor sees, every page being in review).
- **Two pictures printed a figure their sentence does not say.** `gas/s2s-in-s2in-alabama` printed 28.43 where the sentence says 28.42, and `tariffs_policy/res-price-res-price-hi` printed 404.8 where it says 404.7: the card holds each value rounded to six decimals (28.424999999999997 became 28.425). Every picture is now drawn from the draft's CSV at full precision, and no picture is written unless the figures it prints are the sentence's.
- **The code is not landed.** `card_image.py` and the new `redraw.py` are on `wip/9820-findings-charts`, row 8 of `docs/state/landing_request_desktop_w4.md`, marked requested. The pictures already on main were drawn by that branch's code.

## What was done

- **Part 1, the 76 drafts whose sentence the audit mended** (the audit counts 78 "passed after a fix"; seven of those fixes were to the do-file only and one draft was withdrawn; comparing every draft's sentence with the line drawn in its picture finds exactly 76 that differ): each drawn again from its own card and CSV with the sentence as the `.md` now says it, its printed figures checked against the CSV and the sentence before writing.
- **Part 2, the forty of the sheet:** each opened and looked at before and after. Faults found, all at the chart code (`warehouse/analysis/findings/card_image.py`), one change for every draft: the first year's label sat on the line where the line starts (most charts); the marked figure sat on a falling or jagged line (about a third); the Texas cold chart's legend lay across the 2026 line, and the brand file asks for each series named on its line, not a legend; no ink zero line where zero is on the scale (the one color rule broken; no color outside `docs/brand.md` was drawn); years the table does not hold drawn one step apart (uranium of US origin skips 2019, 2020 and 2022); the marked year without an axis label; the events' day ticks put Jan 31 beside Feb 01. No title, sentence or source line was cut or ran off the picture; they are now wrapped by measured width anyway.
- **Part 3, the drafts that passed the audit, strongest first** (by the hunt's strength): all 335 drawn, so 444 charts in all, every draft that passed the audit (with or without a fix) and the five of part 1 the audit could not check. The 105 not drawn are the 90 other drafts the audit could not check, the 13 held on internal tables and the 2 withdrawn.
- **What the measurement found on the 444 pictures as drawn before:** the first year's label on the line, 149; the marked figure on the line, 120; the marked year without an axis label, 119; zero on the scale with no ink zero line, 82; the old words of a mended sentence, 76; missing years drawn one step apart, 20; a legend where the brand file asks for names on the lines, 23 (5 of them over the data); a printed figure that differed from the sentence, 2; nothing found, 93. No text was cut off and no color outside the brand file was drawn. Every one of the 444 was opened and looked at after it was drawn, ten to a contact sheet.
- **The review:** https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/findings-charts-2026-11-20.md, one row a chart: what was wrong, measured on the picture as drawn by main's old code (its labels, legend, lines and axis read back), and what was done.
- **The tool:** `warehouse/analysis/findings/deep/redraw.py` (`fetch` reads every draft's card from public.scanner_drafts, read only; `draw` and `check`).

## Decisions made without you

- Every draft of the sheet was drawn again even where nothing was found, so that the forty read as one set; a row says when the picture came out the same.
- A marked figure with no clear place beside its point goes to the nearest clear place with a thin cardinal leader to the point (the COVID-19 Tennessee chart, the one such case so far); any other label with no clear place is placed where it crosses least and the render says so.
- The pictures inside each Supabase row and the 1080 px squares keep the old drawing: no write to Supabase was made (writes are refused, and none was asked).
- Part 3 starts with the 33 of the sheet not in part 1, then the rest by strength; a row of part 3 is a picture drawn again with its faults listed.

## For Samuel's ruling

- **Chart titles** name the subject, not the finding: left as they are, as instructed.
- **A first year standing alone:** in the pipeline-capacity drafts (`gas/s2s-in-*`), 1990 is held, then nothing until 1994; the sentence compares with 1990. The old charts hid the gap; the new ones show it.
- **The square pictures and the Supabase copies** keep the old drawing until a run rebuilds them.

## Snapshots

| Push | Before | After | Differences |
|---|---|---|---|
| Every push of images, b01 to b45 (rows 1 to 444 of the review) | `s9820-bNN-before` | `s9820-bNN-after` | 0 in all, each push (expected) |

## Needs the key

- Nothing.
