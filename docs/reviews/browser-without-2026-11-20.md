# What a browser would complain of, found without one, 20 November 2026

Energy Research Warehouse (ERW). Chain 610, part D (`queue/done/610-night-20-november-oldlaptop-weekend-pack-security.md`), sessions 9816 to 9819 in the desktop's third window. No browser was run. Two reads: the source on `origin/main` at `26dfe42cc`, and the HTML of 138 addresses (every page and view of `check-values.mjs`'s list, one address each, with the pages it leaves out) read from production once each, a second apart, as a reviewer reads them (the internal view opened by the form, no script run, DNT and `x-erw-check: 1` sent, so no usage was counted). The scripts are in `runs/c610w3/` of this window's worktree (not in git): `links_static.py`, `a11y_static.py`, `headings_static.py`, `headings_cross.py`, `read_pages.py`, `html_a11y.py`.

## Links and printed addresses

- **Every site path the source names**, against the 178 routes and redirects and the 1,492 files of `site/public`: 158 in `href`s and the menu, 252 string literals naming a site path, 20 links in the documents the site renders, 26 in the site's data files. **None broken.** Six were not matched and each is no link: a query appended to a page (`/cost-of-power` with its query), and five prefixes of the release list or templates (`/api`, `/internal`, `/reports`, `/data/methods`, `/data/standard`). Two folders the build writes into `site/public` (`analysis-files`, `digest-charts`) are not in git and were taken as present.
- **Every full address a page prints** (`https://erw-flame.vercel.app/...`): `/api/download` (46, the readers' downloads) and `/research`, both routes that exist.

## Names, alternatives, headings, contrast

| # | Page | What a checker would say | Fixed | Row |
|---:|---|---|---|---:|
| 1 | `/policy?view=week` | each button of the week grid is named only by its number ("3, toggle button"); its meaning is in a hover a screen reader never reads | named by the hover's words (`aria-label`) | 9 |
| 2 | `/policy?view=week` | a count of zero drawn in the muted color at 40 percent opacity: about 2 to 1, below the brand's 4.5 to 1 for text (`docs/brand.md`) | full strength, 5.6 to 1 | 9 |
| 3 | `/severance` | the credit's tier list in the calculator has no name | "Credit tier, <option>" | 10 |
| 4 | `/data/licenses` | two h1: the page's and the rendered `docs/licenses.md`'s | the note's headings one level down (`render(..., { under: true })`) | 11 |
| 5 | `/map?tab=resources` | two h1: the tab's and the rendered `docs/methods/resources.md`'s | as row 4 | 11 |
| 6 | `/map?tab=queues` | the page's h1, then an h3 ("Every entry year") | an h2, the same look | 11 |
| 7 | `/grid` (the reliability table) | a year with no days drawn as "." in the rule color, about 1.4 to 1, and read as "dot" | the muted color, 5.6 to 1, read as "none" | 12 |
| 8 | `/policy` | no h1 | **already fixed on a branch waiting to land**: the portable laptop's `wip/9601-policy-held-page`, in row 4 of `docs/state/landing_request_window2.md` (chain 620's ten fixes). Not redone | (row 4 of window 2) |

**Found sound:** no `<img>` without `alt` in the source or the HTML; every `<svg>` of the source is hidden from screen readers, named, or carries a title; no button, link or form control in the 138 pages' HTML without a name; no heading skipped or doubled in any other page; the text colors of `site/app/tokens.css` pass 4.5 to 1 on the page and on fog (the brand file's table), and the other faint colors the source uses are fills, disabled controls or hidden drawings.

## What this read cannot see

- What the browser draws after the page's script runs: a control that appears only after a click (the tier list of row 3 was found in the source, not in the HTML), a chart drawn by the chart library, the menu's links in the internal view (drawn as text until the script knows the view). `site/scripts/a11y-axe.mjs` and `check-links.mjs` on a build see those; the landing desk's gate runs the second.
- Contrast where a color is computed at run time: the week grid's heat cells (`/policy?view=week`, the accent mixed with white at 8 to 50 percent) behind ink text give 11.9 to 1 at the palest and 4.86 to 1 at the darkest, so every count passes; a chart's series colors are fills, named in the chart, its hover or its table (the brand file's rule), and were not each computed.
