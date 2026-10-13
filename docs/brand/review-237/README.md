# Review 237: the Grid tool, one page at /grid

Session 237, 13 October 2026, branch `wip/237-grid` (from `a4c54722`; not on `main` when these were taken).
The page at `/grid`, in the internal view, on a local production build of this branch (`runs/session237/shots.mjs`).
JPEG, the top 5,000 px of each page at most, so the folder stays under 4 MB; a page taller than that is cut at the foot.

| File | What it is |
|---|---|
| `ercot-now-1280.jpg`, `ercot-now-390.jpg` | `/grid?grid=ercot`: the Now view of ERCOT (the sentence, the three numbers, the mix in that hour, then what ERCOT's page showed) |
| `ercot-network-1280.jpg`, `ercot-network-390.jpg` | `/grid?grid=ercot&view=network`: the Network view, the 3D network (the default), ERCOT's panel open |
| `ercot-network-map-1280.jpg`, `ercot-network-map-390.jpg` | the same view with the toggle on "Map" (`shape=map`) |
| `ercot-mix-1280.jpg`, `ercot-mix-390.jpg` | `/grid?grid=ercot&view=mix`: the Mix view (the mix page, "Where the power comes from", the table of every region) |
| `ercot-clean-1280.jpg`, `ercot-clean-390.jpg` | `/grid?grid=ercot&view=clean`: the Clean view ("How clean", the emissions page's three blocks, "How clean, and when") |
| `ercot-exchange-1280.jpg`, `ercot-exchange-390.jpg` | `/grid?grid=ercot&view=exchange`: the Exchange view |
| `ercot-ask-1280.jpg`, `ercot-ask-390.jpg` | `/grid?grid=ercot&view=ask`: the Ask view, ERCOT's own question box (no question was sent) |
| `pjm-now-1280.jpg`, `pjm-now-390.jpg` | `/grid?grid=pjm`: the Now view of PJM |
| `us48-now-1280.jpg`, `us48-now-390.jpg` | `/grid?grid=us48`: the Now view of the Lower 48 |

Read in the browser with each screenshot: no page scrolls sideways at either width, every page carries the brand's wrapper,
no page shows the word "undefined" or "NaN", and no script error was thrown (18 pages).
