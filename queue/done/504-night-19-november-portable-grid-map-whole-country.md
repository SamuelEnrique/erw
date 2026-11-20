# Chain of 19 November 2026: sessions 8600 to 8799, portable-laptop (code role), unattended, fifteen hours straight: the Grid tool's map of every balancing authority with the trading on it, the whole country in the Grid tool, then the natural resource map

machine: code

Written by Claude in chat with Samuel on 19 November 2026 at about 02:40 PST and pasted by him into this session. It is not a machine's successor file, and no machine writes a successor to it. Folder: `$HOME\Documents\erw`. Model: Fable, high effort. One Claude Code session. Samuel wants this laptop building for fifteen hours without a gap.

## Why this chain

The 3D network of balancing authorities is the part of the ERW people remember: an energy economist at Stanford told Samuel nobody has shown balancing authorities that way. On 10 October Samuel asked for its companion: a map of the balancing authorities, the ERW's own, as a toggle on the same page, with the trading between them visible on the map. It has not been built. Tonight the data machine (chain 501) writes the boundaries and the page files for all thirteen regions, and this laptop is the one that can build the site and look at it. The Grid tool still offers seven grids; after tonight it offers the country.

## Rules

- **The owner's rules of 16 November 2026 hold word for word** as written in `queue/done/303-night-16-november-portable-trackers-done-line.md` (its rules 1 to 11), with these changes:
- **Session numbers** 8600 to 8799, each checked free on origin/main and every branch first.
- **This machine does not land and writes no warehouse table.** Code for landing is one row marked requested in `docs/state/landing_request_portable.md`, which the data machine's desk lands. A data fault is one row marked requested in `docs/state/data_requests_done_line.md`.
- **A site build** only in the foreground and only with 2 GB of memory free, as in `queue/done/305-night-16-november-portable-done-line-and-browser-reads.md`.
- **Its pages are `/grid` and the new `/resources`.** `/events`, `/demand` and `/supply` are the old laptop's tonight (chain 503); the industry and AI energy pages are the desktop's second window's (chain 502). None of those is edited here.
- **Add, never change.** The 3D network stays the centerpiece of `/grid` and opens first, exactly as it is. Nothing it shows today moves: a test pins the seven grids' figures on the page, and the snapshots show 0 differences on what exists. Every page stays in review. No ruling is taken for Samuel.
- **Samuel's standing rulings on this page hold:** light mode only; the free-floating 3D look is kept (a dark, map-pinned redesign read to him as "for children"); carbon intensity is the color at all times, green clean and red dirty, with no color tabs; names show on hover only; the "Watch" stories, the click-a-grid side panel and the Batteries switch stay.
- **The page standard** is rule 9 of `queue/done/302-day-16-november-oldlaptop-large-load-on-the-site.md`: an upgrade drops nothing, hover tips only, facts and no view, plain nouns, held values drawn blank, every figure sourced, no sideways scroll at 390 px, dense, informative, usable, and everything answers to the mouse.
- **The brand** is `docs/brand.md` as it stands (Source Serif 4, IBM Plex Sans, Plex Mono for numbers, white page with fog panels, thin lines). No new brand decision is made here, no logo, no motion video.
- **Everything is seen before it is claimed:** each view at 1280 and 390 px in a real browser, with a screenshot under `docs/reviews/grid-map-2026-11-19/`.
- **Never end idle before Samuel takes the laptop.** After part D, part E, and the queue step after each page of it.

## Restart safety and the progress file

- The first session writes `queue/next/540-resume-chain-504.md`, committed alone and pushed, and removes any other `*-resume-chain-*` file of this laptop from `queue/next/`. Its text is the lines between BEGIN and END below, without those two words. A session that takes a resume file first writes the same text under the next number up (to 549). The chain's last session removes it.
- `docs/state/progress_c504.md`: one line a view, a row or a page, its state and session, pushed after each.

BEGIN
# Resume of chain 504

machine: code

Chain 504 was interrupted. This file is the portable laptop's: another machine leaves it where it is. First put this same text back in queue/next/ as the next number up to 549, named NNN-resume-chain-504.md, committed alone and pushed. Then read queue/done/504-night-19-november-portable-grid-map-whole-country.md whole and docs/state/progress_c504.md, and continue chain 504 from the first step not marked done, under that file's rules, with the next free session number in its range. Write no other queue file.
END

## Part A: browser reads for the old laptop (the start of every session, twenty minutes at most)

The old laptop cannot build the site. Every row in state `wanted` in `docs/state/browser_reads_wanted.md` whose branch has landed is read on production with the internal cookie at 1280 and 390 px; a row not yet landed is read on a build of its branch if time allows. Each row marked `seen` with what was read, or `fault` with what was seen instead. No row waiting: one line, then on.

## Part B: the map of the balancing authorities on `/grid`

- **The files:** the boundaries are the data machine's `site/data/regions/ba_boundaries.json`, in the contract `docs/state/page_files_regions.md` (on main since 02:30 PST). Checked at the start of each session, never waited on: until the file is on main, read it from the data machine's newest branch that holds it, or code against a small fixture in the contract's form and say so in the progress file. The flows are the file the 3D network already reads (`site/data/grid_network.json`), so the two views can never disagree.
- **A toggle, "Network" and "Map",** at the top of the tool. Network is what opens. The choice is kept in the address, so a link opens the same view.
- **The map:** every balancing authority as its territory, colored by its carbon intensity at the hour shown, on the same scale as the spheres. An authority with no boundary in the file is listed beside the map by name, not dropped.
- **The trading on the map:** the flow between each pair of neighbors at the hour shown, drawn so direction and size read at a glance (width by megawatts, movement along the direction of flow where the motion is the data), from the same numbers as the network. Hover on a flow: both names, the megawatts, the hour, and which side reported it.
- **The same controls in both views:** the hour and "play a day", the "Watch" stories, the Batteries switch, hover for a name and its figures, click for the side panel that says who supplies that authority. A view switched in the middle of a story keeps its hour.
- **Usable on a phone:** at 390 px the map can be moved and zoomed with a finger and nothing scrolls sideways.
- **Performance:** the map view is interactive within three seconds on this laptop and does not load until it is chosen; the measured times go in the report.
- **Tests** that pin: the two views show the same megawatts for the same pair and hour; the carbon scale is one scale; the network view's markup is unchanged when the map has never been opened.
- Landing requested when the map is whole, not piece by piece.

## Part C: the whole country in the Grid tool

- Wherever the tool lets a reader choose one of the seven grids, the thirteen regions can be chosen too, the six the site has never shown among them (the Southeast, Florida, the Carolinas, Tennessee, the Northwest, the Southwest), from `site/data/regions/index.json`, `mix/<region>.json` and `trade/<region>.json`.
- The Mix tab for a region: the generation by source, hourly and by month, in the form the tab has for a grid. A part of the tab the region's file does not hold (a forecast, a price) is drawn blank with a hover that says it is not held for that region, not hidden.
- Clicking a region on the map or the network opens it. Where a region and one of the seven grids cover nearly the same ground and differ, the hover says why in one sentence, from the data machine's method note.
- Ask, the chat, is not changed: it needs the key.

## Part D: the natural resource map, `/resources` (when `site/data/resources/` is on main; checked each session, never waited on)

- Samuel's idea of 7 October: one simple map of every kind of energy resource as switches: sun, wind, geothermal heat, hydropower potential, oil and gas, coal, uranium, critical minerals. The resource itself, not what has been built on it (the project map shows what is built).
- One page, in review, listed on `/in-review` and placed in the Infrastructure group as Samuel's menu of 12 October has it. Each switch is one layer from its file; several can be on at once; hover gives the place, the value, its unit and its source; a short line under each switch says what the measure is in plain words.
- To the done line in the form of chain 303 (method note, replication of one layer's figures from its public source, cross-check against the publisher's own map or table, decisions block).

## Part E: after part D, until Samuel takes the laptop

- The reader's read of each new view (five real cases a named reader would bring: a transmission planner, a power trader, a student of one grid, an AI lab's siting analyst, a battery developer), each taken start to finish in the browser, every gap a numbered row in `docs/reviews/grid-map-read-2026-11-19.md`, every fault fixed at its cause with a test.
- Then the done line for the map and for the regions in the Grid tool, in chain 303's form.
- Then part A again and whatever it finds.

## The last session

- `docs/state/note_2026-11-19_portable_c504.md` in short bullets: what a reader of `/grid` can now do that they could not, with the screenshots' addresses; the regions added; the state of `/resources`; the browser rows read; what waits for Samuel with the default taken, in plain words.
- `.venv\Scripts\python.exe scripts\chain_queue.py next`, and the file it prints run the same way. No file: part E goes on. Samuel closes this session himself.
