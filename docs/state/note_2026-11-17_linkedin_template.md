# LinkedIn post template, 17 November 2026

Unattended session. Model spend USD 0: no model API was called. Nothing was posted or published anywhere, and
`site/lib/release.ts` was not touched.

## What landed

Status: in progress (the landing gate is waiting for the build lock). This section is completed when the branch lands.

- 09:10 UTC: the gate still waits for the build lock, held by another window's gate (`c370-gate-n`) since 08:30.
- 09:35 UTC: the gate of `bd124795e` (the branch merged with main) passed freeze to check_cross_checks; check_csp running. A follow-up from Samuel (new source line, square master re-rendered) waits for the gate to end, then goes through a second gate.
- Branch: `wip/linkedin-post-template`, first commit `686d69920` (the patch applied unchanged, the lock file, the spec
  and the four render files).

## The four render files

All in `docs/research/motion/posts/`:

- `queue_withdrawn_post_2160x2160.mp4` (h264, 2160 x 2160, 450 frames, silent)
- `queue_withdrawn_post_2160x2160_last.png` (2160 x 2160)
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

`numbers.projects` is 22348, the figure "22,348" in the source line. No difference, so the spec was not edited and both
masters were rendered.

## How it went

- Step 1 said to check out main in the repository. The main checkout held another agent's uncommitted work under the
  data lock (`c370-152`), so the branch was made from `origin/main` (`1dc009dad`) in a separate worktree,
  `../erw-linkedin`, and the main checkout was left as it was.
- `git apply` warned about trailing whitespace: the patch's files have CRLF line ends. They were applied as they are,
  since the patched code is not to be changed.
- `npm install` added only the three `@fontsource` packages to `motion/package-lock.json` (30 lines). It noted that
  esbuild's postinstall script was not run; the bundle and both renders worked without it. The first render downloaded
  Remotion's Chrome Headless Shell (120 MB, outside the repository).
