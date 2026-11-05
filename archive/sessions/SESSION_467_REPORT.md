# Session 467 report: the datacenter tracker on the power side

21 October 2026, about 09:06 to 09:35 UTC, unattended, on portable-laptop (the code role; the chain was written for samueloldlaptop, and the queue gave it to this machine), in the worktree `C:\Users\samen\Documents\erw-467` on `wip/467-468-datacenters` (from `origin/main` at `440a2c8f`, with `origin/wip/015-land` merged at `0d459f78`). The chain of 21 to 22 October, night (`queue/done/019-night-21-october-code.md`, session 467). Model spend USD 0; no warehouse data written; no web request (one read of the ERW's own live set to try the new query). Not landed: the database gate was closed (`scripts/db_probe.py`, 3.32 s at 09:27 UTC against 3 s), so there was no build, no after shot and no check-values run.

## Read these first

- **`/datacenters` has a section "On the power side: the sites a public source names"** (`site/app/datacenters/PowerSide.tsx`). Since 21 October `datacenter_facilities` is held whole, so the section never reads it: it reads the queue positions that name a datacenter or a large load from each ISO's own queue table in the live set (`site/lib/data.ts`, `queueSites`), with the builder's own pattern (`QUEUE_PATTERN` of `warehouse/derived/datacenter_facilities.py`) and grids (`QUEUE_ISOS`). A queue that is held itself (ISO-NE's, MISO's, NYISO's) is named and not read. Tried against the live set at 09:20 UTC: 2 sites, both ERCOT's (`ercot_queue:25INR0688`, Giga Texas Data Center, Travis County, 133 MW asked, completed; `ercot_queue:28INR0499`, Alpha Digital Campus, Reeves County, 58.26 MW asked, active), the same 2 rows session 441 counted (`docs/reviews/sources-by-row-2026-10-21.md`, read from `origin/wip/441-450-third`: not landed, so the page applies the rule by its own sources, the queue tables, as the chain allows).
- **Its cost figure is the calculator's own.** For each grid with a site, every load zone with what a flat load paid over the calculator's last twelve complete months, bought as the calculator buys it (real time where held, else day-ahead): `regionCosts` in `site/lib/datacenter.ts`, checked equal to `/cost-of-power`'s headline for every region of every grid (`scripts/datacenter-ways.mjs`, `pageOf`). ERCOT on this machine's files: from USD 33.43 (LZ_HOUSTON, real time) to 38.86 per MWh (LZ_CPS, day-ahead), October 2025 to September 2026; LZ_NORTH, the calculator's default, 33.73.
- **No site is placed in a load zone.** ERCOT's queue states a county, not a zone, and ERCOT publishes its load zones only as a picture (`site/data/curtailment/zone_shapes.json`, session 149's rule): the section says so and shows every zone. The row's "Load zone" reads "not stated by the queue".
- **Epoch AI's data on AI data centers is linked as theirs**, at the address the repository already records (`docs/paper/related_projects_notes.md`: `https://epoch.ai/data/data-centers`); no request was made to it.

## What to review

- The branch: `https://github.com/SamuelEnrique/erw/tree/wip/467-468-datacenters`, commit `f59837eb`.
- After the landing: `https://erw-flame.vercel.app/datacenters#power-side`.
- The method note's new section: `docs/methods/datacenter_facilities.md`, "The power side (session 467)".

## Checks

Every gate redirected to a file under `runs/chain_019/s467/` (git ignores `runs/`), never piped; the exit code read before the next step.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 467"` | 0 | passed (the machine already on duty from the parent's checkout: noted, not an error) |
| `tests.test_session467` | 0 | 11 tests OK: the pattern and grids are the builder's; the section never names the held table; every region's figure equals the calculator's headline (to 9 places, every grid); ERCOT shows load zones only, LZ_NORTH marked; check-values knows `dcpow`; the note names every key as `check-methods.mjs` reads it; the server trace carries the price files; no dash |
| `tests.test_session467.TheReader` with the pattern changed | 1 | 1 failure, as it should |
| `tsc --noEmit` | 2 | 13 errors, none in a changed file: Next's generated `PageProps` and `LayoutProps` and the generated `content/` files, which exist only after a build |
| The 51 tests that read the changed files, and `test_session409` | 1 | 766 tests, 2 not this session's: `test_session102` (scipy's DLL blocked on this laptop by an Application Control policy) and `test_session153` (`content/docs.json` absent in a new worktree; after `npm run content` it passes, exit 0) |
| Build, check-values, snapshot, after shots | not run | the database gate was closed (above) |
| Impeccable | not run | not installed on this laptop (`~/.claude/skills` holds no `impeccable`) |

Shots before, from production at 1280 and 390: `docs/brand/review-467/before/` (the page's top, where "license needed" stands since 21 October).

## Decisions made without you

1. **`origin/wip/015-land` merged first**: it adds the keys section of `docs/methods/datacenter_facilities.md` (session 409) that this session extends.
2. **The public-source rows are read from the queue tables, not from `datacenter_facilities`**: the held table cannot be read by the site, and a queue position's fields are public whatever else names the site. This is the page's own sources column (the facilities' `kinds`), as the chain allows while session 441 is not landed.
3. **Every load zone of the grid is shown, not a nearest one**: no source the ERW holds places a Texas county in a load zone, and session 149's rule forbids drawing one from a picture.
4. **A new key family, `dcpow|<grid>|<region>|per`**, recomputed by check-values with the calculator's own steps; the queue's MW are `entity|` keys of the queue tables.
5. **A grid whose prices are held shows no price** (today the held grids' queues are held too, so none is drawn).
6. **The section is drawn whatever the facilities read says**, below the words about the list and above the source line.

## For Samuel's ruling

- Whether a county list of ERCOT's load zones from another public document (an ERCOT protocol section or a utility's tariff) may place a site in a zone; until then every zone is shown.
- `lib/license.ts`' `gridOfEntity` reads `nyiso_queue:1630` as no grid, so a table held by grid would not hold a queue row by its id (no page reads such a row today; `datacenter_queue_positions` is not in the live set).

## To finish

On a machine with this branch, when `python scripts/db_probe.py` exits 0 (with session 468's landing):

```bash
cd site && npm run build > ../runs/chain_019/s467/build.out 2>&1; echo "exit=$?"
npm start -- -p 3467 &   # then
node scripts/check-values.mjs http://localhost:3467 > ../runs/chain_019/s467/values.out 2>&1; echo "exit=$?"   # CHECK_VALUES_PAGES=/datacenters
node scripts/check-methods.mjs http://localhost:3467 > ../runs/chain_019/s467/methods.out 2>&1; echo "exit=$?"
node scripts/shot.mjs "http://localhost:3467/datacenters#power-side" ../docs/brand/review-467/after/datacenters_1280.png 1280 900 "[data-power-side]"
node scripts/shot.mjs "http://localhost:3467/datacenters#power-side" ../docs/brand/review-467/after/datacenters_390.png 390 844 "[data-power-side]"
```

Then the landing with the snapshot before and after (the combined landing of the chain).

## Files

- `site/app/datacenters/PowerSide.tsx` (new), `site/app/datacenters/page.tsx`, `site/lib/data.ts`, `site/lib/datacenter.ts`, `site/next.config.ts`, `site/scripts/check-values.mjs`.
- `docs/methods/datacenter_facilities.md` (a section added).
- `tests/test_session467.py` (new).
- `docs/brand/review-467/before/` (two shots) and its README.
- This report.
