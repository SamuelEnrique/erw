# Session 1175 report: the network component, lighter on a phone

24 October 2026, from about 01:15 UTC, on samueloldlaptop (the code machine, the old laptop), the twelfth session of `queue/done/078-day-24-october-code-grid-tool-2.md`. Branch `wip/1175-grid`, cut from `wip/1174-grid`, worktree `C:\Users\lossa\Documents\erw-1175`. Code, tests and documents only: no build, no server, no browser (chain 078's brief).

## Read these first

- **The 3D shape's code was already loaded only when that shape is drawn, and was before this session.** Its libraries, 3d-force-graph and three.js, are imported in exactly one place: two `import()` calls inside the network component's own effect (`site/app/network/Network.tsx`, `const load = () => Promise.all([import("3d-force-graph"), import("three")])`). That effect returns before them unless the shape shown is the network (session 180: `if (shape !== "network" || ...) return;`), the browser draws WebGL, and the frame is within 200 px of the screen (session 428, an `IntersectionObserver`). The map and gravity shapes are `next/dynamic` modules of their own (session 180) and import neither library.
- **Which shapes exist and where each opens.** Three shapes, `lib/networkMap.ts` `Shape`: `map`, `network` (the 3D scene), `gravity`. The address's `shape=` sets it; without one the Network tab opens on `network`, the Gravity tab on `gravity` (the page passes `shape="gravity"`, session 299). `/grid` opens on the Mix tab (`DEFAULT_VIEW = "mix"`), which draws no network component at all; the Clean, Now and Ask tabs neither.
- **What only the 3D shape needs**: the two libraries and their packages (below), and the scene's own code in the component (`nodeObject`, the load effect, the update effect, `focusOn`), a few kilobytes.
- **So nothing heavy was left to split.** Moving the scene's own code into a module of its own would take those few kilobytes off the component, against four older tests that pin it where it is (`test_session93`, `237`, `241c`, `428`: the scene's import line, `readPalette(box.current);`, `backgroundColor(PAL.ground)`, `__erwGraph`); extending, never removing, an assertion rules that out. Kept in place (decision below).
- **What the session added:**
  - **The proof**: `site/scripts/test-network-split.mjs` walks the import graph of `app/grid/page.tsx` and the root layout with the site's own TypeScript parser (static imports, `export ... from`, `require`; type-only imports left out, as the compiler erases them), following every relative and `@/` import: 7 tests. No module the page loads statically imports three.js, 3d-force-graph or a package built on them; no package the page imports depends on three.js at any depth (the installed `package.json` files read); the only imports of the two are the two `import()` calls in `Network.tsx`, each inside `load`, inside a `useEffect` whose body checks the shape, then WebGL, then imports, and whose dependency list is `[shape]`; `NetworkMap` and `NetworkGravity` import neither; the Mix tab draws no `NetworkView`. A planted `import { Scene } from "three";` in `Network.tsx` failed it ("app/network/Network.tsx imports three statically"), then removed.
  - **The light placeholder**: while the scene's chunk is on its way, the frame says "Loading the 3D network." over its middle. The frame is the same box (`min(72vh, 620px)` high, at least 420 px: no layout shift). The library empties its element when it draws (`domNode.innerHTML = ''` in 3d-force-graph and three-render-objects), so the line is the box's sibling, laid over it in a `relative` wrapper (`data-scene="loading"` or `"ready"`), never its child; it goes once the graph is built (`setSceneReady(true)` after `graph.current = g;`) and comes back if the reader leaves the shape and returns. `pointer-events-none`, so it takes no drag. The "This browser cannot draw 3D" fallback, the hint line and what the scene draws are unchanged.
  - **The method note**: `docs/methods/grid_network.md`, a section "The 3D scene's code, loaded when it is drawn (sessions 428 and 1175)", with its decisions.
- **The estimate of the gain, not a measurement** (no build): the modules behind the split, walked from their ESM entries through the junction (`3d-force-graph/dist/3d-force-graph.mjs`, `three/build/three.module.js` and what they import), each minified with Next's own terser: 366 modules, 5.17 MB on disk, 1.83 MB minified, about 494 KB gzipped. three.js alone (`import("three")` takes the whole namespace, so nothing of it is shaken off): 2.12 MB on disk, 764 KB minified, about 191 KB gzipped. The rest is mostly `three/webgpu` (three-render-objects imports `WebGPURenderer` statically), `polished`, the d3 modules and tween. A bundler shakes part of `three/webgpu` away, so the real chunk is smaller than the sum: session 428 measured it at about 841 KB. That weight is what the Mix tab, the Gravity tab, the Map shape and a phone that has not scrolled to the frame do not load; this session moves no more of it, since none was left on the page's first load.

## What to review

After the landing (none yet; see below), on production:

1. Open `https://erw-flame.vercel.app/internal/open`, paste the token, press **Open the internal view**.
2. Open `https://erw-flame.vercel.app/grid?grid=ercot&view=network` at 390 px. Scroll to the frame: for a moment it reads "Loading the 3D network."; then the network draws in the same box and the line goes. The page does not jump.
3. Press **Map**, then **Network**: the line shows again while the scene is rebuilt, then goes.
4. Open `https://erw-flame.vercel.app/grid?grid=ercot` (the Mix tab) and `https://erw-flame.vercel.app/grid?grid=ercot&view=gravity&shape=gravity` with the browser's network panel open: no request for the 3D chunk.
5. Read `docs/methods/grid_network.md`, "The 3D scene's code, loaded when it is drawn".
6. Screenshots: not taken, no build (chain 078's brief).

## Checks

- Precheck for session 1175: run by the orchestrator, exit 0.
- `node scripts/test-network-split.mjs` (new): exit 0, 7 tests passed. With a static `import { Scene } from "three";` planted in `Network.tsx`: exit 1 on that import; the plant removed.
- Node tests that read the changed files, one at a time: `test-check-revised.mjs` exit 0 (12 of 12); `node --import ./scripts/alias-register.mjs scripts/test-grid-addresses.mjs` exit 0 (without the alias loader it stops on `@/lib`, as its usage line says).
- `python -m unittest`, one module at a time: `tests.test_session1175` (new, 5 tests), `109` (1 skipped), `1153`, `1156`, `1158`, `1167`, `124` (4 skipped), `168_network`, `180`, `193`, `237`, `241c`, `266`, `299`, `412`, `428`, `473`, `54`, `583`, `93` (2 skipped), `1162`, `1165`, `1170`, `1171`, `1172`: each exit 0. No assertion changed.
- `npx eslint app/network/Network.tsx scripts/test-network-split.mjs`: exit 0, one warning that was there before (the `priceMax` memo's dependency list).
- Type check through the junction (`mklink /J` to the main checkout's `node_modules`): `npm run content` exit 0, `npx next typegen` exit 0, `npx tsc --noEmit -p .` exit 0; the junction removed with `rmdir` (the main checkout's packages intact).
- The estimate: a scratch script (not committed) walking the two libraries' ESM imports and minifying each module with `next/dist/compiled/terser`: exit 0.
- No build, no server, no browser, no check-values run, no screenshots (chain 078's brief). No Supabase read was needed.

## The landing

- None in this session: chain 078 is code only, and chain 077's landing B (`wip/1162-grid`) is not on main (its gate was stopped by a low-memory reap). This branch stacks on it and lands with it. Pushed: `wip/1175-grid`.

## To finish

- **The first load at 390 px, before and after**, with chrome-devtools-mcp, unattended, no other build or Chrome beside it: `emulate` (viewport 390 by 844, mobile, touch; CPU throttling 4x), then `performance_start_trace` with a reload and `performance_stop_trace`, on `/grid?grid=ercot&view=network`, `/grid?grid=ercot` (the Mix tab) and `/grid?grid=ercot&view=gravity&shape=gravity`. Before: production (`https://erw-flame.vercel.app/...`, internal view). After: landing B's build on a local server. Write LCP, total blocking time, the script time of the largest chunks and whether the 3D chunk was fetched before any scroll; then scroll the network frame into view and record the chunk's request and the moment the line goes. Session 428's figures at 390 (blocking time 2,196 to 734 ms) are the earlier reference. Expected: no 3D chunk on any of the three before a scroll; the Network tab's numbers within the machine's noise of production's, since this session moved no code off the first load.
- **`next build`'s route sizes before (main) and after (landing B's build)** for `/grid`. If Next 16 prints no size columns, read instead the size of each chunk the served HTML of `/grid?grid=ercot&view=network` names (`.next/static/chunks/`), before and after, and the transfer sizes from the trace.
- Land `wip/1175-grid` with the chain's combined landing: `scripts/land_check.py --ref <the combined branch>`, the snapshot before as its own command, the push to `task/`, the snapshot after once production shows the new commit, `compare`. Expected differences: the served HTML of the Network tab of each grid (and of a `shape=map` address, which the server draws as the network until the browser reads the address) gains the wrapper `data-scene="loading"` and the line "Loading the 3D network."; in the browser the line goes once the scene is drawn; no number, no key.
- At that landing, `node scripts/test-network.mjs <the local site>` and `node scripts/check-network-v3.mjs <the local site>`: the scene's canvas is still found in the box by its label (`[aria-label^="A 3D network"]`), and `__erwGraph` is still on the box.

## Decisions made without you

- **The scene's own code stays in `Network.tsx`.** The libraries were split in session 428; what is left is a few kilobytes, pinned where it is by the tests of sessions 93, 237, 241c and 428. A module of its own would mean changing their assertions.
- **The proof is a source scan with the TypeScript parser**, not regular expressions: a comment or a string holding "three" cannot be read as an import, and a type-only import (erased by the compiler) is left out.
- **The scan covers the whole page, not only the default tab's modules**: every module `app/grid/page.tsx` and the root layout reach, whichever tab draws them; a stronger claim than the default tab's, and one that holds as tabs change.
- **The loading line is words, not a drawing**: no grey shape or fake sphere stands in for the network. It sits over the box as its sibling, since the library empties the box.
- **The line is drawn on the server too** (the scene is never drawn there), so the served HTML of the Network tab carries it; it is listed as an expected difference above.
- **The chunk failing to load still shows "This browser cannot draw 3D"** (the existing `.catch`), kept as it is, as the session asked; see the ruling below.

## For Samuel's ruling

- On a phone the Network tab opens on the 3D shape and fetches its chunk (about 841 KB) once the reader scrolls to it; opening phones on the Map shape instead would spare it unless chosen. Recommendation: keep as is (the address and the Gravity tab already choose), or rule a phone default.
- When the 3D chunk fails to download (a dropped connection), the frame says the browser cannot draw 3D, which is not the cause. Recommendation: a second sentence for that case ("The 3D network could not be loaded; the Map shape draws the same ties"), a words change for you to rule.

## Files

- New: `site/scripts/test-network-split.mjs`, `tests/test_session1175.py`, this report.
- Changed: `site/app/network/Network.tsx` (`sceneReady`, the wrapper and the loading line; the scene, its imports and its fallback unchanged), `docs/methods/grid_network.md` (the section "The 3D scene's code, loaded when it is drawn (sessions 428 and 1175)").
