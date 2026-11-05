# Session 540 report: shadcn MCP and Bencium, evaluated, nothing installed

21 October 2026, unattended, on samueloldlaptop (the code machine), in the worktree `C:\Users\lossa\Documents\erw-540` on `wip/540-s` (from `origin/main` at `24f40c4c`). Chain 024 (`queue/done/024-night-21-october-code.md`, session 540), the roadmap's item 4, "Tooling". Model spend USD 0; no pull from any publisher; no warehouse data written; no site build (none needed, and the machine is short of memory tonight). Nothing installed, no MCP server added, no settings file edited, no package downloaded.

## Read these first

- **The note is `docs/reviews/tooling-shadcn-bencium-2026-10-21.md`.** Both answers are no. shadcn's MCP server only searches registries and hands back source code and an `add` command, but every tool needs a `components.json`, and the setup that writes it adds a second theme beside `site/app/tokens.css` (radius 0.625rem, a `.dark` block, `tw-animate-css`, OKLCH colors) and five dependencies. The site has nothing it is for: 32 files with a native `<select>`, 30 with `<details>`, one `role="dialog"`, no combobox, tabs or popover. Bencium's nineteen plugins (commit `5de46a39`, unchanged since session 201 read it): the controlled designer "ALWAYS ASK"s, the typography plugin silently applies em dashes and curly quotes and forbids underlined links (three clashes with `CLAUDE.md` and `docs/brand.md`), and the design audit reads `DESIGN_SYSTEM.md`, `PRD.md` and five more and writes `progress.txt` and `LESSONS.md`. Its fifteen dimensions are kept in the note as a checklist to read by hand.
- **One thing found that is already installed:** UI/UX Pro Max's `ui-styling` skill (plugin 2.13.0) tells a session to run `npx shadcn@latest init` and `add`, and its `shadcn_add.py` runs `npx shadcn@<version> add`. The script refuses without `site/components.json`. Right now that missing file is the only guard. `docs/tooling.md` gains one line saying a session does not run it and no session creates that file.
- **Requests: 24, each named in the note's table**, by `curl`, with the ruled contact string as the user agent and one second between requests. Robots files came first for ui.shadcn.com, github.com, raw.githubusercontent.com (none, 404) and docs.github.com. **One fault of order:** npm's registry (`registry.npmjs.org/shadcn/latest`, request 11, metadata only) was read before its robots address (request 24). That address holds no robots file: it answers the metadata of an npm package named `robots.txt`. The test found the fault, and the note says so.

## What to review

- The note: `https://github.com/SamuelEnrique/erw/blob/wip/540-s/docs/reviews/tooling-shadcn-bencium-2026-10-21.md`
- The new line at the end of `docs/tooling.md` ("shadcn MCP and Bencium are not installed").
- `tests/test_session540.py`: the note answers both tools, has at most 25 requests numbered in order, reads each host's robots file first (the one late host named), contains no em dash and no personal address, and has three ruling items, one a line. `docs/tooling.md` points to the note.
- The fetched pages, kept off git: `C:/Users/lossa/Documents/erw/runs/chain_024/s540/fetched/` (01 to 24).

## Checks

Each gate's output went to a file under `runs/chain_024/s540/`, never piped, and its exit code was read.

| Check | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 540"` | 0 | on duty until 2026-10-22 11:51 UTC |
| `tests.test_session540`, first run | 1 | the table's regex missed row 16 (text after its address); regex corrected, not the note |
| `tests.test_session540`, robots order | 1 | npm's registry read before its robots address; request 24 made and the fault written in the note |
| `tests.test_session540` | 0 | 7 tests OK |
| `tests.test_session216`, `tests.test_session401`, `tests.test_session540` (the modules that read `docs/tooling.md`) | 0 | 23 tests OK |
| The whole suite, `ERW_LOCK_EXEMPT=1 ... -m unittest discover -s tests` (`suite.out`) | 0 | 5,211 tests OK, 291 skipped; none of the known failures of this machine (156, 484, the page-file tests) failed this time |

No build, no server, no screenshot: no page was touched.

## Decisions made without you

- The note pins the Bencium files to commit `5de46a39b4640fa419560cd0b67e4c4b50dac802`, the commit the repository page named tonight. The innovative designer was not read again: the commit is the one session 201 read.
- `bencium.io` was not read. The plugins' license (MIT) is in the repository, and GitHub's terms (request 23) govern reading it.
- One line was added to `docs/tooling.md` (reversible) so that a later session does not follow the `ui-styling` skill into `shadcn init`.
- The roadmap's item 4 is not ticked in `docs/roadmap.md`. Its "done" includes this note, but ticking it is left to the orchestrator or to you.

## For Samuel's ruling

- Install the shadcn MCP server: the note recommends no; a widget hard to write by hand is copied from the public registry's source onto tokens.css instead.
- Install any Bencium plugin: the note recommends no, typography above all (em dashes, curly quotes, no underlined links).
- Turn off UI/UX Pro Max's `ui-styling` skill at the user level (it says to run `npx shadcn@latest init`), or keep the new line in docs/tooling.md as the guard.

## To finish

Nothing waits on this session. Session 542 merges `wip/540-s` with the chain's other branches.
