# Session 7402 report: the datacenter tracker's decisions block

Energy Research Warehouse (ERW). Chain 303, portable-laptop, 16 November 2026, about 09:33 to 09:39 UTC. Model spend: USD 0.

## What was done

- **Checked first:** `/datacenters` carried no decisions block on origin/main (`/deals` carries one of session 465, in another form).
- **Twelve decisions** (`site/lib/decisions.ts`, `DATACENTER_TRACKER_DECISIONS`): what a sum counts; megawatts only as stated; a sum of every basis; a range or a ceiling; a queue's megawatts; status only where stated; the grid of a facility; when two rows are one facility; the views by operator; ERCOT's figures in words; the timeline's wait; the hold. Each has its **default** and its **source**.
- **On hover:** the shared block (`site/components/tool/DecisionsBlock.tsx`) draws the default and the source as the site's own tip (hover, tap or keyboard focus), only where a list gives them. The five tools' lists give neither, so their pages are drawn as before; a test holds that.
- **Where:** at the foot of both views (`/datacenters` and `?view=grids`), before the source line, as the battery page carries its own, with a link to the tracker's method note. Words only, so it is drawn under the hold.
- **The note carries the same list word for word** (section 12); `tests/test_session7402_trackers.py` holds the two equal (8 tests).
- **Checks:** type check of `app/datacenters/` and what it imports, 0 diagnostics. The test files that name the block, the list or the page: 71 pass. A wider run of 210 test files gave 5 failures, the same 5 on main at `e83dd0e06` without this stack (`test_session1011`: the site's copy of `llms.txt` is two days behind the package's; `test_session143`, `148`, `156` and `161`: the Thesis Builder's Node tests). None is this stack's.

## Decisions made without you

- The decisions list is "the handful that move the figures" (twelve), not every choice of every session.
- The block's title says "each with its default and its source on hover", not the five tools' "each with the session that made it".
- No build on this laptop (1.7 to 1.9 GB free): the block was not read in a browser. The landing's build on the data machine is its first.

## For Samuel's ruling

- None new.

## Commit

- `wip/7400-trackers`: `8ae74bfef`.
