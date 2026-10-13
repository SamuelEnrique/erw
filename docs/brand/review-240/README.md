# Session 240: top blocks on /board and /datacenters

Screenshots in the internal view, local builds in the worktree of branch `wip/240-top-blocks`, 13 October 2026. Each
is the window (1280 by 900, or 390 by 844), not the whole page; none is quantized (the folder is under 2 MB).
`facts.txt` holds, for each, the page's width against the window's (no sideways scroll at either width), its height,
and the counts of tiles, folds and rows.

| File | What it shows |
|---|---|
| `after_board_top_1280.png`, `after_board_top_390.png` | /board on the brand: the twelve tiles, the strip of eight, "Jump to", the first group open |
| `after_board_group_1280.png`, `after_board_group_390.png` | "Natural gas" opened by its title; the closed groups under it, each with its count and its first number |
| `after_datacenters_top_1280.png`, `after_datacenters_top_390.png` | /datacenters on the brand: the three numbers under the title, "What changed this week" |
| `after_datacenters_group_1280.png`, `after_datacenters_group_390.png` | the list by operator: the filters, the first group open, a second group opened. Taken one commit before the branch's last: here "Operator not stated" is the first group, on the branch it is the last |

**No "before" screenshot is here.** The base commit was not built: the build mutex did not come back to this
session in its time. `archive/sessions/SESSION_240_REPORT.md`, "To finish", has the one command that takes them.

What to look at:

1. /board, the twelve: each tile's name, value with its unit, its date, "Day" and "Week" with an arrow and a sign (up in
   cardinal, down in green, as the wall's moves), and the trend of its last 30 points. A click on a name opens the
   workbench on that row.
2. /board, a closed group: its title, its row count and its first number stay in view.
3. /datacenters, the second number: what the sum counts, and its split by status as the table has it ("status not
   stated" is the table's blank).
4. /datacenters, the third number and the section under it: what is held (the first story's date) and what is not (a
   change of status or of megawatts), in words.
5. /datacenters, the list: one head a group, the largest operator by megawatts first, the rows with no operator stated
   last.
