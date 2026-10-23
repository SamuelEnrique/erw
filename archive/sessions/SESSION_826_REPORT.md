# Session 826 report: the tracker's A and B

23 October 2026, 08:49 to about 08:56 UTC, unattended, on portable-laptop (the code machine), in the worktree `C:\Users\samen\Documents\erw-826` on `wip/826-deals` (cut from `wip/825-deals`). Chain `queue/done/080-night-23-october-portable-landing-deals-.md`, session 826. Model Fable 5.1. Precheck: session 825's mark (the chain's one duty). Model spend USD 0. No warehouse data written; no request.

## Read these first

- **Two shown deals side by side on the deals tab** (`site/app/deals/Compare.tsx`): the pair in the address (`/deals?a=<deal>&b=<deal>`) through a GET form of two selects over the shown rows, the battery page's A and B form (the same rows, two columns, a "What differs, B against A" row), no verdict. Rows: date, type, parties, asset, technology, grid (from the state), MW, term, USD, USD per MW, status, the evidence's publisher with the other outlets as a count.
- **Keys**: MW and dollars carry the table's (`dealpub|<id>|mw`, `|dollars`); USD per MW, the one figure computed here and only where the deal states both, carries `dealpub|ab|<id>|usd_per_mw`, which `check-values` recomputes from the live set's row. The fixed address `/deals?a=deal:70bf30d372e1d674&b=deal:d6eda0ffd6db76cd` (Vistra's loan beside Amazon and AEP's 960 MW) is in its page list.
- **A held id in the address draws nothing** and says so; the same id twice says so.

## What to review

- `/deals?a=deal%3A70bf30d372e1d674&b=deal%3Ad6eda0ffd6db76cd` (internal view): the table; "Reset the comparison" back to `/deals`.

## Checks

| Check | Exit | Result |
|---|---|---|
| `tests.test_session826` (4) and `tests.test_session825` (8) | 0 | 12 OK |
| `npx tsc --noEmit` | | 0 errors in the deals files |

## The landing

Not yet: `wip/826-deals` pushed; lands with sessions 822 to 827 from the last branch of the line.

## Decisions made without you

1. The comparison is a server-rendered GET form (no JavaScript needed, a link shares it), not the battery page's client-side state: the deals are rows, not assumptions a reader edits.
2. Only the shown rows can be chosen: a held id is refused with a sentence.

## For Samuel's ruling

- Nothing new.

## Files

- New: `site/app/deals/Compare.tsx`, `tests/test_session826.py`, this report.
- Changed: `site/app/deals/page.tsx`, `site/lib/dealspublic.ts`, `site/scripts/check-values.mjs`, `docs/methods/energy_deals.md`.
