# Sessions 1907 and 1908: the W45 Roundup's rows 68 and 63, their open parts (chain 219, 13 November 2026)

Energy Research Warehouse (ERW). Chain 219, sessions 1907 and 1908, samueloldlaptop, unattended, Opus 5.5. In the worktree `erw-1907`, `wip/1907-periodicals` cut from `wip/1903-stack` (`0c2853246`) and `wip/1908-periodicals` on top of it. About 01:55 to 02:05 UTC, beside session 1903's gate. All in `warehouse/news/roundup.py`; no table or Supabase write, no model call, no site build. Run ahead of sessions 1904 to 1906 (they need the landing) while the gate held the build lock.

## What it did, with commits (branch head `7604f300d`)

- **Row 68, its second choice (session 1907):** with no plant the week's stories name, a category with no new observation read "in its place, the week's next price move: WTI Cushing crude closed at 99.64 USD/bbl ...", a second oil price beside Brent's. Now: "in its place, policy: <title> (<agency> <kind>, published <date>), the Policy of the Week below.", keyed on the Tables line ("the policy, `policy_actions` <event_id>"); capacity still first, a second price only when neither is held. `policy_of_the_week` and the new `policy_pick` read one order (`week_policy`). `838e20e94`.
- **Row 63, its open part (session 1908):** session 1894 read `energy_deals` only. Where no row matches, a stored Digest's item (`docs/digest/YYYY-MM-DD.md`, dated before the week) with two of the story's parties and the same MW, else the same sum of a million or more, makes the story a step: "A step in a story first carried before this week: the Digest of 2026-10-14, item 1 ("Google signs 20-year PPA with AEP for 702 MW Wyoming fuel cell project")." and the gap "what the week's step changes in that story; the 702 MW is the outlets' figure, not a warehouse table's."; it ranks below the week's first reports. The table's row still comes first. `c0fe49992`.
- The faults file's states of rows 63 and 68 (`7604f300d`).

## Tests

- `tests.test_session1907` 11, `tests.test_session1908` 15, with `test_session1894` and `test_session1895`: 64 tests OK (`runs/s1907/t1907.out`, `runs/s1908/t1908.out`). The whole suite in session 1903's second gate: 8633 tests OK, 368 skipped.
- Landed with session 1903's stack as `b1bc8829f`; the branches deleted.

## Decisions made without you

- The policy stand-in names the Policy of the Week and says it is below, rather than a second policy action: the most significant one is the one the five should carry, and the words say why it appears twice.
- Only the Digests are read for row 63: they print each item's parties and figures; the Roundups print neither, so their items cannot be matched without guessing.
- A sum under USD 1 million in a Digest's fields is taken for a price, not a deal ("$106.37 per barrel").

## For Samuel's ruling

- None new. Rows 39 and 65 stay the owner's.
