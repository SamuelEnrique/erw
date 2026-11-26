# Session 10407 report: chain 720, part E: what the second window's read of the two pages found

Energy Research Warehouse (ERW). 26 November 2026, the portable laptop's first window (code role), unattended.

## The read

- The second window read `/forecast` (43 addresses) and `/equities` with the board's group (19 addresses) on production after the landing of 17:13 UTC, at 1280 and 390 px (`docs/reviews/browser-read-2026-11-26.md`).
- **What it found right:** every marked figure agrees with the files (38,042 on `/forecast`, 832 on `/equities`); nothing on `/forecast` can be taken for an operator's or a published figure; a loss is drawn as a win is; a held price is a blank with its reason; the board lost nothing it had (25 groups and 276 rows before, 26 and 306 after); every control is named and the keyboard reaches the foot.
- **What it filed for this window:** four rows. Each is mended at its cause, with a test.

## The four rows

- **FC1, the hour a forecast was made could not be read on a phone or with the keyboard.** It was in a mouse's hover alone. Beside each place's name under "Tomorrow" there is now the site's own small mark, which opens on a hover, a tap and the keyboard's focus and says when the forecast was made, what figures it rests on and by which method. Row 60.
- **FC2, the hover gave the file's hour beside the rule's hour with no word between them.** Mended earlier, on row 57: the hover says the two differ and which one it gives.
- **FC3, a held price's hover said its status twice** ("License needed: license needed: PJM's prices ..."). It is said once. Row 60.
- **EQ1, the first blank of `/equities` read "license needed" over a hover that began "source needed".** The face and the hover's first words now name the same status. Row 61.
- **FC4 is not the page's:** one day's demand differs between the forecast's file and the demand page's file for the Southeast (a data fault; the second window filed it to window A as data request 575).

## A mistake of this window's own, found on the way

- Two of this window's earlier test lines pinned the faults themselves: one held the status said twice, one held the hover's old order. Both now hold the mended words. A test that copies what the page prints, instead of what it should print, lets a fault through; the review's reader caught what the tests had approved.

## Tests

- `/forecast`: 127 and 131 checks in the two Node tests; the Python tests pass. Built and tried: a tap at 390 px, the mouse and the keyboard's focus at 1280 px each open the mark.
- `/equities`: 104 and 24 checks; every drawn figure against main's files, 1,092, none differing.

## Decisions made without you

- **The mark is the site's own "i" mark,** the one the decisions of other pages use, placed beside the place's name. The page's general hovers (a blank's reason, a chart's "source") are left as they are: whether every hover of the site should open on a tap is line 1 of the review's rulings for you.
- **The walking tests were not run again for these two rows:** each changes existing files only and adds none.

## For Samuel's ruling

- The review's line 1 (a reason on hover and a finger), which is the whole site's and not these pages' alone. Today: these pages' other hovers answer a mouse only.

## Needs the key

- Nothing. No model was called.
