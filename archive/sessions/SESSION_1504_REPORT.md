# Session 1504 report: every page read on a build; the links, the values and AccessLint

Energy Research Warehouse (ERW), session 1504, chain 158, samueloldlaptop, 6 November 2026, 10:57 to 11:13 UTC. Model: Claude Opus 5.5 (this window's). Model spend USD 0. No warehouse data written; nothing sent or posted; web requests to the ERW's own database (the local build's reads) only. On main (this report; no code changed).

## What it did

- A local production build of main at `19826ad7` (sessions 1486 to 1503 landed; `npm ci` on `next` 16.4.5), served on port 3504.
- **`check-links.mjs`, every page in the internal view in a real browser**: 734 pages, 40,446 links, 2,204 addresses. 11 findings, 1 link waiting for a ruling, 3 aliases by design, 0 pages not read cleanly.
- **`check-values`**: the two gates of this chain's landings read every page's keyed figures on the same code: 7,793 of 7,793 values match the live set, with the floors of `/deals` and know-your-grid failing on main and production alike.
- **AccessLint (`audit_live`), in the internal view**: the browser was given the internal view by the form at `/internal/open` (`runs/s1504/unlock9222.mjs`; the token posted, never in an address). Ten pages, each the default view at 1280: the battery, the generator, the datacenter tool, the three explorers, the board, the datacenter tracker, Ask (`/grid?grid=us48&ask=1`) and the home page. **8 with no violation, 2 with one serious each.** The phone's width was read by device metrics for the tools and the explorers by session 1499 (390 px everywhere).

## The findings, by owning chain

| Finding | Page | Owner |
|---|---|---|
| a scrolling region not reachable by keyboard (`figure > details > div`: add `tabIndex={0}` and a name) | `/cost-of-power` | the datacenter tool (the desktop's chains 155 and 157 are wiring its All grids tab) |
| a scrolling region not reachable by keyboard (`#other > details > div > div`) | `/board` | the price board |
| 6 downloads answer 404: the research cards' pictures (`/findings/siting_*_1080x1350.png`, `_1600x900.png`) for the battery swing, flexible and gigawatt cards | `/research/card/siting_*` | the siting cards (the desktop's) |
| 2 links to `/findings/` answer 404 ("Python", "Stata do-file") | `/research/card/siting_gigawatt` and 2 more | the same |
| 3 anchors `/data#<table>` that `/data` does not hold (`eia_padd_rail_barge_movements_monthly`, `eia861m_utility_sales_monthly`, `onrr_revenue_monthly`) | the Digest's chart sections of 22 and 23 October and `/digest` | the periodicals (chain 161): the tables are not in the live set's list on `/data` |

None of the eleven is on a page this chain changed. This chain's pages (the three explorers, the replication files, the paths' documents) read clean.

## Decisions made without you

- AccessLint on ten pages, not all 225: one call a page, and the ten are the five tools', the explorers' and the paths' pages. The links ran on every page.
- AccessLint's own headless Chrome (it was already on port 9222) took the internal view by the form; it and the server were stopped after (no browser left running).

## For Samuel's ruling

- None (the findings are their chains' to fix).
