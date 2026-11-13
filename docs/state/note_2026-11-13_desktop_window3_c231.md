# Note: the licensing sweep continued, 13 November 2026 (chain 231, lab-desktop third window)

Energy Research Warehouse (ERW). Written by session 4163 of chain 231 (`queue/done/231-day-14-november-desktop-window3-licenses-continued.md`). Sessions 4150 to 4163, 11:55 to about 12:45 UTC, the day after chain 229 (`docs/state/note_2026-11-13_desktop_window3.md`), whose work and rulings this note does not repeat. Model spend USD 0. Nothing sent, nothing posted, no warehouse write, no site build. Reports `archive/sessions/SESSION_4150_REPORT.md` to `SESSION_4163_REPORT.md`.

## What moved

| | Chain 229's end | Chain 231's end |
|---|---:|---:|
| Publishers confirmed on their current page | 37 | **162** (none with its sentence gone) |
| Verdicts cut again from a changed page, the verdict unchanged | 1 (Berkeley Lab) | 3 more (IESO: its years; the U.S. Drought Monitor: new words; Berkeley Lab's stays) |
| Requests in the record | 1,805 | 2,057 (252 this chain: robots files and current pages) |
| Not settled / waiting for a ruling / disagreeing | 26 / 24 / 0 | 26 / 24 / 0 |
| Tables on a read older than 30 days | 36 | 36 (all on hosts that refuse the reader, or paused, or a page 404) |
| Requests of window A | 15 | 27 |

- **Every publisher with a table is now confirmed on its current page,** except:
  - MISO (paused);
  - the hosts whose robots files refuse Anthropic's agents or the ERW's reader: CFTC, Bloomberg, Data Center Dynamics, Hart Energy, Heatmap News, Reuters, Meta, Equinix, OilPrice.com, Utility Dive, ANS Nuclear Newswire, pv magazine USA, Hydrogen Insight, the Texas Comptroller;
  - the FT (its page 404);
  - COSIT and ANEEL (timed out).
- **No flag changed;** no table was held or released.

## Found

- **Robots wildcards:** `urllib.robotparser` reads `*` and `$` literally, so a rule such as the Texas Comptroller's `Disallow: /*/` looked allowed. `scripts/license_confirm.py` now reads wildcards as the convention does and keeps the stricter answer.
  - **All 196 pages** the two chains read were checked again: none was refused.
  - Three of window A's modules use the parser alone (request 27).
- **More outlets refuse Anthropic's agents,** and the ERW's news ingest reads their feeds: OilPrice.com, ANS, pv magazine USA, and Utility Dive's owner (requests 23 to 26).
- **Seven table headers say a read has not happened** where the record holds a verdict (requests 16 to 22).
- **The landing requests:** rows 1 to 3 are superseded by row 4 (`wip/4150-licenses`, origin/main merged), since main's `package/llms.txt` moved. None had landed by 12:30 UTC.
- **The request file's table** had lost its line breaks when rows were added; rebuilt.

## The rulings waiting

- **Chain 229's list stands unchanged:** `docs/state/note_2026-11-13_desktop_window3.md`, "The rulings waiting". No newer rulings file.

## Landing

- **Row 5:** `wip/4151-licenses` (chains 229 and 231 whole, `origin/main` merged at 12:30; 479 test files: 3,116 passed, 101 skipped, 0 failed).
