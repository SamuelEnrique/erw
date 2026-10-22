# Session 715 report: the brand pass

22 October 2026, from 10:31 UTC, on samueloldlaptop, unattended, in the worktree `C:\Users\lossa\Documents\erw-715` on `wip/715-allgrids` (cut from `wip/714-allgrids`). Chain `queue/done/050-night-23-october-code-allgrids.md`, session 715. Model spend USD 0. No warehouse data written; no request to a publisher.

## Read these first

- **The tab is restyled to `docs/brand.md` in `app/tokens.css` only.** The page files gained no style of their own, only data attributes for the rules to find. Structure, density and every number are kept.
- **The changes, each a brand rule**:
  - Text is sans (section 1): the words a figure's cell holds where there is no figure ("not held", "license needed", "no capacity market"), a utility's name, and the small labels in a cell ("rt", "firm", "off", "load:", "MW coming", "annual"). Figures stay IBM Plex Mono.
  - Every tip is sans at the captions size (12 px), on fog with a rule-colored edge (section 6, the hover card).
  - A column head's tip keeps its dotted rule in captions grey on the white header (section 5: no colored band).
  - A tip in the first four columns opens to the right; a tip opening left was cut by the table's frame. A tip sits above the row heads that stay in place.
- **Already in place from the brand's shared rules**, and kept: the header without a band, mono figures right-aligned, the first column in place while the table scrolls, the fade at the edge it continues past, and the fog box.
- **For Samuel to rule from**: before is 712's build (`docs/brand/review-706/after_allgrids_*.png`, `review-709/after_nodes_*.png` and `review-702/after_electrolyzer_*.png`, all taken before this pass); after is this build, `docs/brand/review-715/`: the hub table, the node list and the electrolyzer profile, at 1280 and 390.

## What to review

1. Compare `docs/brand/review-706/after_allgrids_1280.png` (before) with `docs/brand/review-715/after_allgrids_1280.png` (after): the cells' words in sans, the labels small and sans, the figures mono.
2. After the landing: `https://erw-flame.vercel.app/cost-of-power?view=allgrids`, hover any figure: the tip is fog with an edge, in sans.

## Checks

| Check | Exit | Result |
|---|---|---|
| precheck | 0 | |
| `tests.test_session715`, `714`, `237` | 0 | OK (every rule closed: the merge of 714's and 715's appended blocks lost a brace, the known trap, and it was restored and checked) |
| `db_probe.py` | 0 | 0.73 s |
| `npm run build` (lock `s715`, beat), timed | 0 | 64 s, then 32 s warm |
| check-values, `CHECK_VALUES_PAGES=/cost-of-power` | 0 | 2,487 of 2,487 |
| `check-existing-tab.mjs`, production against the build | 0 | 0 differences |
| AccessLint after the restyle (714's scan, on this build) | 0 | 0 findings |

## The landing

Sessions 713 to 715 land in one push from this branch; see below once done.

## Decisions made without you

1. **Data attributes in the page, rules in `tokens.css`**: the chain's rule that only the tokens and the shared components carry style. Tailwind's layout classes already in the page stay.
2. **Labels inside a cell are sans at 12 px**: the brand's 12 px is for captions and notes, and these are a cell's notes.

## For Samuel's ruling

- The brand shots, `docs/brand/review-715/`, for the restyle as a whole.

## Files

- Changed: `site/app/tokens.css` (the tab's block), `site/app/cost-of-power/AllGridsView.tsx` (`data-util-name`, `data-opens`).
- New: `tests/test_session715.py`, `docs/brand/review-715/`, this report.
