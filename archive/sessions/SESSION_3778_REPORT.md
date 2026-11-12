# Session 3778 report: the accessibility audit chain 211 carried (the pages in the internal view, with axe-core)

Energy Research Warehouse (ERW). Chain 212, data machine (lab-desktop), 12 November 2026 13:34 to 13:42 UTC. Opus 5.5. Model spend USD 0. Requests: none to any publisher. A local build of main at `53d8a2f69` (chain 211 landed), served on port 3212, read in the machine's own headless Chrome; production not touched.

## Read these first

- **One WCAG 2.2 AA rule is broken, on two pages, and it is older than chain 211:** `target-size` (2.5.8, "touch targets 24 px, or space around them").
  - **The All grids tab** (`/cost-of-power?view=allgrids`): 21 elements at both 1280 and 390 px. They are the tab's tooltip buttons (`Tp`, `data-tip-trigger`) that wrap a truncated row label (`<span class="block truncate ...">`).
  - **`/board`:** 17 elements at 1280 px and 18 at 390. The section links (`#spark`, `#gas flows`, `#gas prices`, `#retailpower`) and the filter buttons (`px-1.5 py-px`).
- **No other rule broken** (WCAG 2.0, 2.1, 2.2, A and AA) on `/datacenter`, `/internal/health`, `/internal/findings` or `/ask`.
- **Chain 211's change to the tab** (text inside the existing `role="tooltip"` span) adds no failing element. The 21 are the row-label triggers, which chain 211 did not touch.
- **The tool:** `site/scripts/a11y-axe.mjs` (new). It uses the axe-core engine the site's packages already hold and drives `scripts/browser.mjs`'s headless Chrome, which opens the internal view by its form (the token never in an address).
  - AccessLint's live audit cannot carry that cookie.
  - Its HTML audit takes the 1.9 MB page as a string.
  - Not a gate.

## What it did

- `git pull --ff-only` in the main checkout (to `53d8a2f69`). The build lock was taken (`c212-s3778`), 7.9 GB free. `npm ci` exit 0; `npm run build` exit 0 (13:35 to 13:37 UTC).
- `next start -p 3212`, then `a11y-axe.mjs` at 1280 px on the six pages chain 211's session 3772 named, and at 390 px on the two with findings. Outputs: `runs/c212/s3778_axe_1280.out`, `s3778_axe_390.out`, `s3778_axe_detail.out`.
- The server was stopped and the build lock released. The build's line-ending rewrite of `site/data/policy/paused.json` was put back.

## Decisions made without you

- **The target-size findings are reported, not fixed.** A fix changes how the tab's table and the board's filter rows look (a 24 px minimum, or more space), a design change for your eye; the tooling rule says findings on structure go to your ruling.
- **axe-core instead of AccessLint** for pages behind the internal view. Both are rule engines; axe-core is already in the site's packages, and nothing new was installed.

## For Samuel's ruling

- **Touch targets on the tab's row labels and the board's filters** (WCAG 2.2, 2.5.8, AA). Recommendation: give `[data-tip-trigger]` and the board's filter buttons a 24 px minimum height in `app/tokens.css` (one rule each), then read both pages at 390 and 1280. Default: unchanged.
