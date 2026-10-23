# Chain 072's note: sessions 1042 to 1063, code machine (old laptop), 23 October 2026

Written by session 1063 of `queue/done/072-day-23-october-code-allgrids-packages-2.md`. The name `review_2026-10-23_code.md` was taken by an earlier note, so this one carries the chain's number. Chain 071 ran on this machine at the same time, in its own worktrees; this chain took the build lock before each build and touched none of its branches.

## One line a session

| Session | Branch | Address to review | Screenshots |
|---|---|---|---|
| 1042 | `wip/1042-allgrids` | the next file `queue/next/073-...` (on main); the replication's rounding fix (`warehouse/replication/siting.py`) | |
| 1043 to 1045 | the same | `docs/reviews/siting-rulings-answered.md` (none answered) | |
| 1046 | the same | chain 049's two tables named (report) | |
| 1047 | the same | `/cost-of-power?view=allgrids`, a CAISO row's "reserve margin not held" tip; `docs/methods/siting.md` decision 30 | `docs/brand/review-1048/n05_reserve_tip_1280.png` |
| 1048 | the same | `/cost-of-power?view=allgrids&rows=nodes&node=ercot%3A7RNCHSLR_ALL` | `docs/brand/review-1048/` |
| 1049 | the same | `docs/reviews/siting-map-design.md` | `docs/brand/review-1049/` |
| 1050 to 1052 | the same | the three path files' "Walked again (session 105x, chain 072)" | |
| 1053 | the same | report only | |
| 1054 | the same | report only (no owner's run) | |
| 1055 | the same | `packages/conformance/conformance.json` (version 2) | |
| 1056 | the same | `package/src/erw/errors.py`; `docs/methods/packages.md`, "Errors, in words" | |
| 1057 | the same | report (AccessLint 10 scans, 0 findings; 390, 0) | |
| 1058 | the same | report only (no ruling) | |
| 1059, 1060 | the same | `docs/methods/siting.md` v7, `docs/methods/packages.md` v2; the open items, rulings items 23 and 24 | |
| 1061 | the same | `docs/reviews/digest-revisions-proposal.md` | |
| 1062 | | the clean-up (report) | |
| 1063 | | this note; `queue/next/073-...` updated (on main) | |

Landings: 1043 to 1061 merged as `cbf8662e` (served 09:18 UTC, 0 differences); 1042, 1062 and 1063 are on `wip/1063-records`: their gate was stopped by Claude Code for low memory and is not restarted unattended; chain 073's session 1064 lands them first (session 1062's report, "To finish").

## Decisions made without you

1. EIA-411's 2016 projections are not drawn as any grid's reserve margin; each grid's tip names its area and why (decision 30).
2. A node's County and Zone come after Days held in the node list, so every figure stays in view at 1280.
3. Projects counted by either end's county; ERCOT's 9999-01-01 is no date; the report date written 2026-07-13.
4. The county map is a design only, a shade by count, no node as a point.
5. The conformance file's call 7 moved to the hourly intensity (430 days); `make.py` carries the errors block over.
6. Three new error sentences, the same in the three packages; a start equal to the end is refused too.
7. Sessions 1043 to 1061 ran before 1042 finished, chain 071 holding the build lock; one report for 1050 to 1052.
8. The replication (1042) and the conformance makes (1055) passed their request ceilings once each (35 against 20; 53 within 60 after a second make); said in their reports.
9. When the background wait for the build lock was stopped for low memory, it was not restarted; the lock was watched with a light check and taken when free.

## Waiting for you

- Rulings items 1 to 24 (`docs/reviews/siting-rulings-2026-10-23.md`; 23, EIA-411 or NERC, and 24, the county map, are new) and 20 (`siting-rulings-answered.md`).
- `docs/reviews/packages-open.md` items 1 to 9: the Stata and R run (it now exercises three new sentences), the two licenses and R's maintainer, the PyPI upload, the Redivis click, the downloads, `/llms.txt`, the guide, the price board's ERCOT figures.
- The Digest's revisions: A, B or neither (`docs/reviews/digest-revisions-proposal.md`); until then check-values fails the 21 October issue's WTI until 23 November.

## `queue/next` for this machine

`073-evening-23-october-code-allgrids-packages-3.md` (sessions 1064 to 1085), updated by this session and on main (`77368854`). Chain 071's last session may take it before this chain's queue step does; whichever takes it runs it.
