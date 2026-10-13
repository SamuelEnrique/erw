# Session 239: the merged pages, each tab, at 1280 and 390 px

Taken on the local build of the branch `wip/239-merges`, in the internal view, with `site/scripts/shot.mjs`
(the window's first 1,600 px of each page, not the whole page). One file a tab and a width:
`<page>-<tab>-1280.png` and `<page>-<tab>-390.png`.

| Page | Tabs |
|---|---|
| `/storage` | fleet, buildout (`?tab=buildout`), owners (`?tab=owners`) |
| `/severance` | calculator, lease (`?tab=lease`) |
| `/prices` | now, ercot (`?tab=ercot`) |
| `/demand` | metered, weather (`?view=weather`), consumption (`?view=consumption`) |
| `/deals` | deals, tracker (`?tab=tracker`), companies (`?tab=companies`) |
| `/map` | projects, resources (`?tab=resources`) |

The tabs are one component (`site/components/tool/Tabs.tsx`), styled by the brand rule that styles the three
cost-of-power tabs (`site/app/tokens.css`, "the tabs").
