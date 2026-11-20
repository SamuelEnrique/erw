# LinkedIn post template, 17 November 2026

Unattended session. Model spend USD 0: no model API was called. Nothing was posted or published anywhere, and
`site/lib/release.ts` was not touched.

## What landed

Landed on main at 11:21:59 UTC as merge commit `256e8b0a0` ("Merge task/linkedin-post-template: checks passed (run
44068123810)"), which brings in the gated commit `4733a9498` (branch `wip/linkedin-post-template`: `686d69920` the
template and first post, `a28ca3088` the follow-up, and two merges of origin/main made by the gate script). The merge
changed exactly these files on main: the four render files, `linkedin_post_template.patch` (removed),
`motion/package-lock.json`, `motion/package.json`, `motion/render_post.mjs`, `motion/specs/posts/queue_withdrawn.json`,
`motion/src/Post.tsx` and `motion/src/Root.tsx`. `site/lib/release.ts` is untouched.

- Gates (`scripts/land_check.py` through `runs/c153/gate_held.sh`, one hold of the build lock with the hand checks):
  `bd124795e` passed every step at 09:35 (hand checks 09:39); `4733a9498` passed every step at 10:42 (hand checks
  10:46). Logs in `runs/land_check/<sha>.txt` and `runs/linkedin/` (not in git).
- Freeze: `scripts/freeze.py status` exit 0 (no freeze) before each gate and before the push. The push was at 10:47
  UTC, outside the 14:00 to 16:15 UTC window.
- GitHub run 44068123810 (code branch): checks passed; main had moved, so the merge job ran the suite again and merged.
- Deploy: Vercel status success for `256e8b0a0`; the live site served its deployment (`data-dpl-id`
  `dpl_FWrTcAyGBznsRBDynPsb9PhyRvL4`) at 11:23:34 UTC.
- Snapshots (CLAUDE.md rule 8): `before-4733a949` (10:47:36 UTC) and `after-4733a949` (11:23:41 UTC), 25 pages each,
  0 failed. `compare`: 0 differences on all 25 pages. Expected: the landing changes no site file, and every page is in
  review. Note that production had already moved between the two snapshots to another deployment
  (`dpl_C5MCz8gcCRD7xHVRhKuMJRvFnCPZ`, other sessions' commits on main); it also showed no difference.
- Nothing was posted or published anywhere.

Progress log of the landing:

- 09:10 UTC: the gate still waits for the build lock, held by another window's gate (`c370-gate-n`) since 08:30.
- 09:35 UTC: the gate of `bd124795e` (the branch merged with main) passed freeze to check_cross_checks; check_csp running. A follow-up from Samuel (new source line, square master re-rendered) waits for the gate to end, then goes through a second gate.
- 09:39 UTC: the first gate and its hand checks passed every step for `bd124795e`. 09:40: the follow-up committed as `a28ca3088`; its gate waits for the build lock (held by `c370-gate-p` since 09:40), as of 10:00.
- 10:18 UTC: the lock was taken and main merged again; the second gate checks `4733a9498` (suite running at 10:25).
- 10:46 UTC: the second gate and its hand checks passed every step for `4733a9498` (suite: 10044 tests, OK, 464 skipped; check_values passed with only the known license-hold floors, /policy). 10:47: freeze status 0; before snapshot `before-4733a949` (25 pages, 0 failed); pushed to `task/linkedin-post-template`. Main had moved by docs-only commits since the gate (clean merge-tree); `task/7052-data-p` in flight trial-merges clean; `task/198-battery-data` (37 days, not judged by the gate) conflicts, as before.

## The four render files

All in `docs/research/motion/posts/`:

- `queue_withdrawn_post_2160x2160.mp4` (h264, 2160 x 2160, 450 frames, silent; re-rendered with the new source line,
  see the follow-up below)
- `queue_withdrawn_post_2160x2160_last.png` (2160 x 2160; re-rendered likewise)
- `queue_withdrawn_post_2160x2700.mp4` (h264, 2160 x 2700, 450 frames, silent; rendered with `--height 1350`)
- `queue_withdrawn_post_2160x2700_last.png` (2160 x 2700)

Both last frames were opened and read: 2160 px wide, the header "ERW Research", the title "Grid connection requests
withdrawn, filed 2000-2020", seven rows in the spec's order ending with Other, every bar the same grey and every number
in ink (nothing highlighted), the rule with the source line under it, and no text cut off.

## The number check

Every row of `motion/specs/posts/queue_withdrawn.json` equals the "Withdrawn" series of
`site/data/findings/queue_divorce.json` (computed_at 2026-11-12T18:02:53Z) exactly, to the last digit:

| Spec label | Findings label | Value (percent of requested MW) |
|---|---|---|
| All Technologies | All technologies | 75.2141195848057 |
| Battery | Battery | 63.95506614918607 |
| Gas | Gas | 79.44978254195402 |
| Solar | Solar | 70.86663828189789 |
| Solar and Battery | Solar and battery | 53.23596506930892 |
| Wind | Wind | 77.39141525501205 |
| Other | Other | 83.92781211146371 |

`numbers.projects` is 22348, the figure "22,348" in the spec's original source line. No difference, so the spec was not
edited and both masters were rendered. (The follow-up below later removed the count from the source line.)

## The follow-up: source line changed, square master re-rendered

At Samuel's request (17 November 2026, while the first gate ran), "source" in
`motion/specs/posts/queue_withdrawn.json` is now exactly: "Source: Berkeley Lab, Queued Up (2026 edition). Share of
requested MW withdrawn by technology, interconnection requests filed 2000-2020, status end-2025. Wind is onshore;
Other includes offshore wind, hydro, coal, nuclear, and geothermal."

- The request count was removed because Berkeley Lab's published count (21,927, from 7 ISO/RTOs and 33 non-ISO
  balancing areas) differs from the file-wide count (22,348, `numbers.projects` in
  `site/data/findings/queue_divorce.json`).
- Wind is onshore only: the findings' method puts offshore wind in Other (its grouping: "Other (hydro, coal, nuclear,
  offshore wind, geothermal, wind and battery, other)"). The new source line does not name "wind and battery" or
  "other", which are also in Other; the text was set as given.
- The seven row values were not changed; the number check above still holds for them.
- `queue_withdrawn_post_2160x2160.mp4` and `queue_withdrawn_post_2160x2160_last.png` were re-rendered (commit
  `a28ca3088`; h264, 2160 x 2160, 450 frames). The new last frame was opened: the new source line under the rule, no
  text cut off, nothing highlighted.
- The 2160 x 2700 files were not re-rendered (only the square master was asked for), so they still carry the old source
  line with "22,348". Rerun `node render_post.mjs specs/posts/queue_withdrawn.json --height 1350` from `motion/` to
  bring them in line.
- The spec's `_numbers_from` field still ends "projects 22348". It is not drawn on the post and was left as it was.

## How it went

- I passed the first gate `--task task/linkedin-post-template`, so its printed push command named
  `task/task/linkedin-post-template`. It was not used: the second gate ran with `--task linkedin-post-template`, and
  the push went to `task/linkedin-post-template`.
- The gate script kept its clean worktrees `../erw-land-bd124795` and `../erw-land-4733a949` (`--keep-worktree`); they
  hold no branch and were left in place, as were `../erw-linkedin` and `../erw-linkedin-note`.
- Step 1 said to check out main in the repository. The main checkout held another agent's uncommitted work under the
  data lock (`c370-152`), so the branch was made from `origin/main` (`1dc009dad`) in a separate worktree,
  `../erw-linkedin`, and the main checkout was left as it was.
- `git apply` warned about trailing whitespace: the patch's files have CRLF line ends. They were applied as they are,
  since the patched code is not to be changed.
- `npm install` added only the three `@fontsource` packages to `motion/package-lock.json` (30 lines). It noted that
  esbuild's postinstall script was not run; the bundle and both renders worked without it. The first render downloaded
  Remotion's Chrome Headless Shell (120 MB, outside the repository).
