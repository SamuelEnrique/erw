# Session 1011 report: llms.txt and the AI reader

23 October 2026, from about 03:28 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-1011` on `wip/1011-packages` (cut from `wip/1010-packages`). Chain `queue/done/070-evening-22-october-code-packages.md`, session 1011. Model spend USD 0. No warehouse data written. Requests: none.

## Read these first

- **`package/llms.txt` opens with a new section 0, from the specification**:
  - the six calls side by side in Python, Stata and R;
  - the three install lines;
  - the backends and `auto`;
  - the types;
  - what a held table does;
  - the citation;
  - the ten tables most readers want first (each public, with what the live set keeps of it).
- **Sections 6 and 9 were corrected**: the backends (the Stanford dataset by default, `live`, `auto`) and what `erw.cite` writes now.
- **The rest is kept.** `llms.txt` is also the chat's system prompt (`/ask`), and its table guidance is what the chat answers from.
- **The chat's briefing was regenerated** (`site/lib/chat/spec.json`, `python warehouse/chat/ask.py --export-spec ...`), and `warehouse/chat/check_spec.py` passes.
- **`/llms.txt` on the site serves the same text**: `build-content.mjs` copies `package/llms.txt` into `site/content/llms.json` (ignored by git), and `app/llms.txt/route.ts` returns it.
  - Test 1011 compares the copy on a build with the file: equal, byte for byte.
  - A path with a file's ending passes the release gate's curtain, so the route keeps the review itself: the internal view gets 200 and the text, a visitor 404 (checked on the build).

## What to review

1. `package/llms.txt`, section 0.
2. `https://erw-flame.vercel.app/llms.txt` in the internal view (after the landing).

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `python warehouse/chat/check_spec.py` | 0 | current |
| `tests.test_session1011` (on the build: the copy byte for byte), `445`, `92`, `156`, `266`, `267` | 0 | 106 tests OK (22 skipped, as before) |
| `runs/check1009.py` (the route's two checks) | 0 | 200 with the cookie and the same text; 404 without |

## The landing

Sessions 1000 to 1014 landed in one push: see `SESSION_1014_REPORT.md`, "The landing".

## Decisions made without you

1. **Section 0 added, the rest kept**, since the briefing is the chat's prompt.
2. **`/llms.txt` for the internal view only** while the site is in review.

## For Samuel's ruling

- **Whether `/llms.txt` may be public before the site opens**: it describes the packages and the tables, and names no key.

## Files

- New: `site/app/llms.txt/route.ts`, `tests/test_session1011.py`, this report.
- Changed: `package/llms.txt`, `site/lib/chat/spec.json`, `site/scripts/build-content.mjs`, `site/.gitignore`, `tests/test_session445.py`.
