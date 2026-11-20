# Chain of 20 November 2026, night: sessions 9200 to 9399, lab-desktop, second window, unattended, until the weekly limit: the codebook, every variable of every table documented, checked by a test and shown where a reader and a program look for it

machine: lab-desktop-window2

Written by Claude in chat with Samuel on 20 November 2026 at about 02:10 PST, uploaded by him to `queue/next` and started by him by name in a SECOND Claude Code window on the desktop. It is not a machine's successor file, and no machine writes a successor to it. The `machine:` line names no role, on purpose: the chain worker and the first window never take this file or its resume file. Folder: `C:\Users\Shared\Documents\erw-w2` (a worktree of the desktop's repository). Model: Opus 5.5, high effort. Run it unattended, to its last session. Do not stop to ask questions. Model spend USD 0: call no model API. No heredocs or long inline scripts: use the Edit and Write tools, and put scripts in `runs/`.

## Why this chain

The Energy Research Warehouse is modeled on the Item Response Warehouse, and what makes that warehouse citable is not its size: every table says what a row is and every variable says what it means, in the same words everywhere. The ERW holds about 700 tables. Each has a method note in prose; almost none says, column by column, what the column is, its unit, its allowed values and where the source calls it something else. The Redivis release is Samuel's click, and the day he clicks, a researcher who opens a table must be able to use it without reading the connector. The `erw` package and the chat read the same descriptions. This is the work that turns a large collection into a warehouse a paper can cite, and it needs no ruling: it documents what is there. This machine holds the data, so the ranges and values can be read from the tables themselves and not guessed.

## Rules

- **The owner's rules of 16 November 2026 hold word for word** as written in `queue/done/301-day-16-november-desktop-open-faults.md` (its rules 1 to 10), with the changes below.
- **The second window's rules** are those of `queue/done/502-day-19-november-desktop-window2-findings-industry.md` and `queue/done/164-day-6-november-desktop-window2-findings-landings.md`: this window writes NO warehouse table and takes NO data lock; it never runs the daily run or a backfill; every site build goes through `scripts/buildlock.py`; it never kills a process it did not start; it works only in its own folder and in worktrees it adds beside it; Python is `C:\Users\Shared\Documents\erw\.venv\Scripts\python.exe` by its full path, and the warehouse's data files in that folder are read, never written.
- **This window does not land.** Code for landing is one row marked requested in `docs/state/landing_request_window2.md`, which the first window's desk (chain 601) lands. Metadata files, the codebook's documents, reports and the progress file are pushed to main directly.
- **Nothing reaches Redivis from this window.** What the draft needs is prepared as files, and applying them to the draft is one row marked requested in `docs/state/data_requests_done_line.md` for the first window. Nothing is released by anyone: the release is Samuel's click.
- **Session numbers** 9200 to 9399, each checked free on origin/main and every branch first. **Its queue step is by name, never bare `next`.**
- **Nothing is guessed.** A label, a unit or a meaning comes from the method note, the connector, the source's own documentation (its robots file and terms read first) or the data itself. Where none of them says, the entry reads "not documented by the source" and the table is listed for a second look. A range or a list of values is computed from the table and dated.
- **The data is not changed.** A column whose name is wrong, or that means two things in two tables, is written down with both meanings; renaming it is one plain line under "For Samuel's ruling". No default moves, no ruling is taken for Samuel.
- **Never end idle.** After part E, part F, until the weekly limit.

## Restart safety and the progress file

- The first session writes `queue/next/631-resume-chain-630.md`, committed alone and pushed. Its text is the lines between BEGIN and END below, without those two words. The chain's last session removes it. Nobody takes it by itself: Samuel restarts this window by name if it stops.
- `docs/state/progress_c630.md`: one line a family of tables, with its counts, state and session, pushed after each.

BEGIN
# Resume of chain 630

machine: lab-desktop-window2

Chain 630 was interrupted. Read queue/done/630-night-20-november-desktop-window2-codebook.md whole and docs/state/progress_c630.md, and continue chain 630 from the first step not marked done, under that file's rules, in C:\Users\Shared\Documents\erw-w2, with the next free session number in its range. Leave this file in queue/next until the chain's last session. Write no other queue file.
END

## Part A: the ground (long end 0:45)

Every table of `warehouse/metadata/coverage.csv`: its license and tier, its columns as the file actually holds them, whether it has a method note, what the data standard (`/data/standard`) already says of its shape, which pages read it, and whether it is in the Redivis draft. Grouped into families. Written to `docs/reviews/codebook-plan-2026-11-20.md`, with the order of part B: the public tables that pages read first, then the other public tables, then the internal ones.

## Part B: the metadata, one file a table (`warehouse/metadata/variables/<table>.yaml`)

- **For the table:** what a row is, in one sentence; its keys; its time zone and what its timestamp marks (the start or the end of the interval); how a revision is kept (its vintage rule); its license and tier; its source with the address; the line to cite it by; the method note's address.
- **For each column:** its name; a plain label a reader outside energy can follow; its unit; its type; the values it takes (the list where it is a short list, the lowest and highest held and the date they were read where it is a number or a time); what a missing value means there; and the source's own name for it where that differs.
- **The same word means the same thing:** a column name that appears in many tables (`ts_utc`, `value`, `iso`, `market` and the like) is defined once, in `warehouse/metadata/variables/_shared.yaml`, and each table's file points to it and says only what is particular to the table.
- Push after each family. A family a session cannot finish in its time is left with a line saying which tables wait.

## Part C: the test that keeps it true

A test that fails when a public table has no metadata file, when a file lists a column the table lacks or misses one it has, when a unit is empty, or when a shared name is defined twice. It reads the tables the way the validator does. Landing requested once part B has covered the public tables that pages read.

## Part D: where a reader and a program find it

1. **On the site:** each table's page under `/data/methods/` shows its variables as a table (name, label, unit, type, values), under what the page shows today. Seen at 1280 and 390 px. Landing requested.
2. **In the package:** `erw.describe(table)` and `erw.variables(table)` return the same metadata; tests; the package's own documentation says so.
3. **For AI assistants:** `llms.txt` and the catalogue the chat reads are rebuilt from the metadata, so that a description is written once.
4. **For Redivis:** the table descriptions and variable labels as the files the uploader needs, with the data request row for the first window. Nothing is released.

## Part E: the codebook as documents

One document a family under `docs/codebook/`, drawn from the metadata by a script, never written by hand: what the family holds, each table in a paragraph, each table's variables. And one index, `docs/codebook/README.md`, with the counts: tables documented, variables documented, "not documented by the source", and names that mean two things.

## Part F: after part E, until the weekly limit

- The internal tables, in part B's form.
- Every entry that reads "not documented by the source": the source's documentation read once more, and the method note's author's intent read from the connector.
- Every name that means two things across tables, listed with both meanings and the tables, as one page for Samuel's ruling.

## The last session

- `docs/state/note_2026-11-20_window2_c630.md` in short bullets: tables and variables documented, by family; what the test now holds; where the metadata shows; what waits for the first window and for Samuel, in plain words.
- The resume file removed. `C:\Users\Shared\Documents\erw\.venv\Scripts\python.exe scripts\chain_queue.py next --file <a file named for lab-desktop-window2, if one waits>`. No such file: part F goes on.
