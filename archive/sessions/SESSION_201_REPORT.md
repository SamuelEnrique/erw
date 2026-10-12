# Session 201 report: the roadmap in the repository, and the tools installed and proven

12 October 2026, unattended, on the old laptop (`samueloldlaptop`, a code machine). Branch `task/201-tooling`. Model spend USD 0, no model call. Pulls: package installs from npm and GitHub only. No data lock, no warehouse data written, no page changed.

Clock: precheck at 08:59 UTC; work until about 09:15 UTC; nothing ran from then to 16:40 UTC (the session was paused; I did not find the cause, and the machine's duty check reads "nothing for 458 minutes"); work again from 16:41 UTC. Working time is inside the long end of 2:30; the wall clock is not.

## Read these first

- **Six tools are installed on this machine, each proven by a run on `/cost-of-power/battery`.** All at the user level of Claude Code, none in the repository. Impeccable is installed without its hooks (first ruling below).
- **No page is live, so each proof ran through the internal view.** A tool that opens the address as a visitor gets the "in review" page (the first chrome-devtools run did). `CLAUDE.md` still says three pages are live; `site/lib/release.ts` says none since session 166.
- **The roadmap is in `docs/roadmap.md`, planner off.** The planner cannot read three of its lines as written (the budget, the Sunday cutoff, the items): rulings 2 to 4.
- **Two tests were pinned and are repaired; one of them made `main` fail GitHub's check every day from 05:00 to 13:00 UTC.** `tests/test_planner.py`: the queue step's test read the real clock against the sample roadmap's start hours.
- **What the tools found that matters for the restyle:** links told from text by color alone (13, every scanner agrees); no focus style defined anywhere; layout shift 0.31 on a phone profile; ten font sizes; cardinal doing nine jobs. Impeccable scores the page 25 of 40.

## What to review

1. The roadmap: https://github.com/SamuelEnrique/erw/blob/main/docs/roadmap.md
   - Read "Status" (seven lines), "This week" (ten items in your order), "Rulings" (thirteen lines dated 12 October), "Holds" (five).
   - Then on a machine with the repository: `python scripts/planner.py check`. It prints "planner: off" and three further reasons (rulings 2 to 4).
2. Which tool for what: https://github.com/SamuelEnrique/erw/blob/main/docs/tooling.md
3. The installs, on the old laptop, in a terminal:
   - `claude plugin list`: two plugins, `accesslint@accesslint` 0.10.3 and `ui-ux-pro-max@ui-ux-pro-max-skill` 2.13.0, both "enabled".
   - `claude mcp get chrome-devtools`: "Status: Connected", scope "User config".
   - `dir %USERPROFILE%\.claude\skills`: `impeccable`, `frontend-design`, `web-design-guidelines`, `vercel-react-best-practices`.
   - Start Claude Code in the repository and type `/impeccable`: it answers with its menu of commands.
4. The proof runs, on the old laptop, under `C:\Users\lossa\Documents\erw\runs\session201\` (`runs/` is not in git):
   - `chrome-devtools-mcp\battery_1280.png` and `battery_390_true.png`: the whole page at 1280 and at a true 390 px.
   - `chrome-devtools-mcp\lighthouse_desktop\report.html`: open in a browser.
   - `impeccable\critique.md`, `ui-ux-pro-max\critique.md`, `frontend-design\critique.md`, `vercel-skills\web-design-guidelines.md`, `vercel-skills\react-best-practices.md`, `accesslint\01_audit_battery.txt`.
5. The two patches, not applied: `runs\session201\claude_md.patch` (text under "The patches" below).

## Part A: the roadmap

- `docs/roadmap.md` holds your content of 12 October under the template's six headings; each heading keeps its "What goes here" line.
- `python scripts/planner.py check`: exit 3, "planner: off", as intended.
- `tests/test_planner.py`, two tests changed:
  - `test_the_roadmap_is_the_empty_template_and_the_planner_is_off` asserted an empty template. It now asserts the six headings, their opening lines, no em dash, and that `check` runs and writes nothing. It no longer asserts "off": turning the planner on would otherwise turn `main` red.
  - `test_with_the_planner_on_the_planned_chain_is_committed_pushed_and_taken` failed at 09:01 UTC: "a session may start from 13:00 to 05:00 UTC". `scripts/chain_queue.py`, `plan()` gains a `now` it hands to the planner; the test passes the fixed time the other tests use. The queue step itself is unchanged (it passes no `now`, so the clock).

## Part B: the installs and their proof runs

| Tool | Version | Install source | Command | Where it is |
|---|---|---|---|---|
| Impeccable | 4.5.2 (engine 0.1.14) | npm `impeccable`, from github.com/pbakaus/impeccable | `npx -y impeccable@4.5.2 install --yes --providers=claude --scope=global --no-hooks` | `~/.claude/skills/impeccable`, four agents in `~/.claude/agents` |
| UI/UX Pro Max | 2.13.0 | github.com/nextlevelbuilder/ui-ux-pro-max-skill (its plugin marketplace) | `claude plugin marketplace add nextlevelbuilder/ui-ux-pro-max-skill`, `claude plugin install ui-ux-pro-max@ui-ux-pro-max-skill --scope user` | `~/.claude/plugins`, seven skills |
| frontend-design | commit `dbd4588f` | github.com/anthropics/skills, `skills/frontend-design` | `npx -y skills@1.7.2 add anthropics/skills -g -a claude-code -s frontend-design -y --copy` | `~/.claude/skills/frontend-design` |
| web-design-guidelines, react-best-practices | commit `063bee94` | github.com/vercel-labs/agent-skills | the same command with `vercel-labs/agent-skills -s web-design-guidelines` and `-s vercel-react-best-practices` | `~/.claude/skills/web-design-guidelines`, `~/.claude/skills/vercel-react-best-practices` |
| chrome-devtools-mcp | 1.10.1 | npm `chrome-devtools-mcp`, from github.com/ChromeDevTools/chrome-devtools-mcp | `claude mcp add --scope user chrome-devtools -- cmd /c npx -y chrome-devtools-mcp@1.10.1 --headless --isolated --no-usage-statistics --no-performance-crux` | `~/.claude.json` |
| AccessLint | plugin 0.10.3, its MCP server 0.11.1 | github.com/accesslint/claude-marketplace | `claude plugin marketplace add accesslint/claude-marketplace`, `claude plugin install accesslint@accesslint --scope user` | `~/.claude/plugins`, five skills and the server |

Every install: exit 0, output in `runs/session201/<tool>/install.out`. The installs wrote `enabledPlugins` and `extraKnownMarketplaces` into the user's `~/.claude/settings.json` (the plugin command's own doing) and nothing into this repository's `.claude/`.

The page for every run: a local production build of this branch (`npm run build`, exit 0), served on port 3201, the internal view unlocked in the tool's own browser; the token is in no file of the runs.

**Impeccable** (`runs/session201/impeccable/`): `critique`, as its playbook asks: a design review and a detector run in two separate agents.
- Found: 25 of 40 on ten heuristics ("acceptable"). Content judged authored for this product; the visual layer generic. Detector: exit 0, 0 findings on 20 files.
- Worth acting on in the restyle: cardinal does nine jobs and the six table header bands are the heaviest ink; numeric columns mix "5.46 million" with "664,224"; the sensitivity chart is in another palette with 6 px bars; Georgia's digits dip below the line in the headline numbers.
- Worth a ruling (structure, not restyle): the inputs that set the headline are in three places and their effect is off screen; a grid picked but not shown is dropped when a Duration is clicked.
- Noise: the detector's zero says little here (it scans markup for patterns; this site's colors and fonts are in one token file it did not read). Three playbook steps were not run: the overlay for a watching person, the snapshot it writes into the repository, its closing questions.
- Caution: its playbooks tell the model to treat "the user is not watching" as untrue and to ask. An unattended session must be told not to, each time.

**UI/UX Pro Max** (`runs/session201/ui-ux-pro-max/`): the plugin's main skill, in a second Claude Code process started for it (a plugin loads only at a start).
- Found: the skill was listed (`ui-ux-pro-max:ui-ux-pro-max`, with six siblings) and its search script ran: 27 searches, all exit 0, Python 3.14.7. 27 findings on the page: 17 a restyle can fix, 2 in part, 8 need markup or behavior.
- Worth acting on first: the base link color in `site/app/globals.css` line 19 sits outside a cascade layer, so it beats every color class on a link. The three tabs ask for ink and grey and all draw in cardinal. Unless it moves into the base layer, the restyle's link colors, and the menu's grey links at the right (session 203), lose the same way.
- Worth acting on in the restyle: field borders at 1.5 to 1 against the field; chart colors written as literals in five files, which a change of `tokens.css` alone will not reach; lining figures set explicitly on the new display face; the year chart's labels at about 6 px on a narrow screen; IBM Plex Mono has no variable file, so each weight is a download.
- Where its data disagrees with direction A: its design-system search returns a dark navy page with a green accent and Fira Code, "always show a legend", and a line for anything over time. The run's reading: keep the plan on all three.
- Noise: most of the search output (marketing page layouts, "Podcast Platform", "Fitness/Gym App", cyberpunk type, native-app rules). The useful parts were its quick-reference checklist and its font rows; the findings came from walking the source and the captures against that list.

**frontend-design** (`runs/session201/frontend-design/critique.md`): the skill has no checker; today's page and direction A were held against its principles.
- Found: today's page is its "trait 1" exactly (cream page, serif display, warm accent); direction A moves away from it (white page, cream as a panel).
- Worth acting on: one type scale of six sizes in place of ten; notes at about 68 characters a line (they run 115 to 135 today); sentence-case labels over the three headline numbers (the capitals are CSS); mono for table figures only.
- Worth writing into `docs/brand.md`: what a rule means, so that the FT-like hairlines stay information.
- Noise: its process for new work (confirm with the client, wireframes, a hero, the copy). The direction, the structure and the words are fixed.
- It agrees with Impeccable on the accent: spent in too many places.

**web-design-guidelines** (`runs/session201/vercel-skills/web-design-guidelines.md`): the page's five files and the two shared components, against the rules it fetched from GitHub (8,055 bytes, kept).
- Found: 33 lines; 17 a restyle can fix, 9 need markup, 1 words, 4 do not fit this site.
- Worth acting on in the restyle: a `:focus-visible` style and hover states (none is defined in `app/*.css`); underlined links in running text; `scroll-margin-top` for the "Scenarios A and B" anchor; a cue that a wide table scrolls sideways; chart text of 10 and 11 units that falls under 8 px on a phone.
- Worth a ruling: ten buttons all named "Reset" for a screen reader; no announcement when the headline or the contract result changes; the year chart has no table of its values.
- Noise: Title Case headings, `Intl` number formats for other locales, "deep-link all state" (the contract's terms are kept out of the address on purpose).
- It reads its rules from GitHub at each use: a pull, in a session whose prompt says none.

**react-best-practices** (`runs/session201/vercel-skills/react-best-practices.md`): 70 performance rules against the same files.
- Found: the page's HTML is 472,966 bytes; `stat()` rebuilds the months on every table cell (over 300 calls for ERCOT, each a full pass); the months travel to the browser as markup and again as component props.
- Worth acting on: `stat()` taking the months already computed (small, no number changes); `content-visibility` on the three folds, with the restyle.
- Later: a Suspense boundary so the header and form arrive before the reads.
- Passes: the two reads are parallel; no heavy library in the bundle; no component defined inside a component.
- Noise: the rules on client fetching, storage, listeners, third-party scripts and animation; the page has none.

**chrome-devtools-mcp** (`runs/session201/chrome-devtools-mcp/`): 30 tools; 16 calls, all answered.
- Found: Lighthouse accessibility 93, best practices 100, SEO 100, on desktop and phone profiles; three failed audits (links by color alone, two radio targets, layout shift). Console: no error, one issue (13 form fields without id or name). 11 requests, none to another host.
- Trace: LCP 382 ms; layout shift 0.068 at desktop and 0.314 on the phone profile, past Lighthouse's 0.25 line.
- Worth acting on: the layout shift, before three brand fonts make it larger; 21 targets under 24 px (nine radios at 13 px).
- For session 203's face check: `resize_page` stops at about 500 px in headless Chrome; a true 390 px needs `emulate` with `390x844x3,mobile,touch` (verified: client width 390, no page-level overflow).
- Noise: Lighthouse's "agentic browsing" score (98 and 69). Screenshots are written only inside a folder the client declares as its root.

**AccessLint** (`runs/session201/accesslint/`): its bundled MCP server, `audit_live`, on the unlocked page.
- Found: 3 violations at WCAG 2.2 A and AA, all one rule: the three download links in the source line are told from the text around them by color alone. No AA contrast violation.
- With AAA rules on: 50, of which 47 are enhanced contrast (7 to 1): muted text on fog 5.14 to 1, muted on white 5.7, the small white line in a cardinal header 6.43.
- Worth acting on: underline links in running text. For the brand: caption grey `#6B675F` will pass AA on white and on fog, and fail AAA on both.
- The "contrast MCP": today's server has four tools (`audit_live`, `audit_html`, `list_rules`, `explain_rule`) and 94 rules; contrast is a rule of the audit (`distinguishable/color-contrast`), not a separate calculator.
- Caution: it left a headless Chrome running on port 9222, holding the internal view's cookie. I stopped it (process 27336, its own temporary profile). Its five skills were not invoked in a Claude session: plugin skills load at the next start.

### shadcn MCP: no, for now

The `shadcn` command (npm, 4.21.4) carries an MCP server (`shadcn mcp`) that searches component registries and adds components to a project. This site has no shadcn: no `components.json`, no Radix, hand-written components over one token file (`site/app/tokens.css`), and `site/AGENTS.md` rules "design tokens: `app/tokens.css` only". Adding it would bring a second styling system the week the brand is being fixed. Not installed. Look again only if the Grid merge needs a widget that is costly to write well by hand (a combobox, a dialog); then one component, restyled to the tokens.

### Bencium UX designer: no; its design audit, later

github.com/bencium/bencium-marketplace (commit `5de46a39`) is a set of plugins. The controlled UX designer rules "ALWAYS ASK before making any design decisions": it cannot work unattended. The innovative one produces ten typography-led directions for a person to lock: the direction is already ruled. Its `typography` plugin applies "correct quote marks, dashes" silently to generated text, which would put em dashes and curly quotes into this repository. Not installed. Its `design-audit` (a phased, visual-only plan) overlaps Impeccable's critique; worth one trial after the battery mockup is approved, if Impeccable's reading proves too generic.

## Part C: `docs/tooling.md` and the patches

- `docs/tooling.md`: which tool for a design critique, an accessibility check, a performance review and a browser check, one line each; the order of use on a page change; seven things every session must know.
- The patches (`runs/session201/claude_md.patch`, 33 lines, `git apply --check --ignore-whitespace`: exit 0, not applied):
  1. `CLAUDE.md`, one bullet at the end of "Key conventions": "Design and browser tools (session 201). On the code machine, at the user level of Claude Code and outside this repository: Impeccable, UI/UX Pro Max, frontend-design, web-design-guidelines, react-best-practices, chrome-devtools-mcp and AccessLint. `docs/tooling.md` says which a session uses for a design critique, an accessibility check, a performance review and a browser check, and what each may not do unattended (no question asked, no `PRODUCT.md`, `DESIGN.md` or `.impeccable/` written, no hook installed, no browser left running). None of them is a gate; their findings on words or structure go under "For Samuel's ruling"."
  2. `.claude/settings.json`, after each `alert.py` line: `"Bash(python scripts/precheck.py *)"`, `"Bash(python scripts/chain_queue.py *)"`, `"Bash(python scripts/duty.py *)"`, and the three `PowerShell(...)` twins, as session 188 proposed.
- To apply both: `git apply --ignore-whitespace runs/session201/claude_md.patch` on the old laptop.

## Checks, with exit codes

None piped; outputs under `runs/session201/`.

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 201"` | 0 | 6 of 6; on duty |
| `scripts/freeze.py status` (at the start, at 16:41 UTC, before the push) | 0 | no freeze |
| `scripts/planner.py check` | 3 | "planner: off", refused, as intended |
| `python -m unittest tests.test_planner` (before the repair, 09:01 UTC) | 1 | 2 failures of 30 |
| `python -m unittest tests.test_planner` (after) | 0 | 30 tests |
| `npm run build` in `site/` | 0 | no "statement timeout" line |
| the six installs | 0 | each |
| chrome-devtools-mcp proof (16 calls), the 390 px test (5 calls) | 0, 0 | all answered |
| AccessLint proof (5 calls) | 0 | all answered (the first try, with a wait condition, exit 1: the condition timed out) |
| `impeccable detect --json`, twice | 0, 0 | 0 findings |
| `git apply --check --ignore-whitespace runs/session201/claude_md.patch` | 0 | applies; not applied |
| Whole suite, clean copy of the merged commit `e6e2247a` (docs, one script and one test file follow it; the report's own tests rerun below) | 0 | 3,445 tests, 237 skipped |

- **Not run:** AccessLint's five skills and UI/UX Pro Max's other six skills in a Claude session; Impeccable's live overlay; any tool on production (every page is in review there).
- **Not verified:** that the tools load on the lab desktop (nothing was installed there).

## The landing

- Freeze status before the push: exit 0, no freeze.
- `main` merged into the branch first (16 commits: sessions 204 and 205 of the data machine, the daily run).
- Before snapshot `s201-before`, its own command, then `git push origin task/201-tooling`.
- Expected: 0 differences on the 25 pages (no file of the site is in the branch).
- **The result, added by session 202's branch:**
  - `take s201-before`: exit 0, 25 pages, 0 failed, 16:58:29 UTC. Push of `8dfa2bfe`: exit 0.
  - GitHub's check ("code branch", run 38281128182): success. Merged into `main` as `b582a777` at 17:05:14 UTC. The workflow removed the remote branch.
  - `take s201-after`: exit 0, 25 pages, 0 failed, 17:34:51 UTC. `compare s201-before s201-after`: exit 0, **0 differences in all** on the 25 pages. Expected: 0. Nothing to mark.
  - **Vercel recorded no deployment of the merge commit** in the 30 minutes after it (read from GitHub's deployment records at 17:34 UTC). It did deploy the two commits before it, at 17:05 and 17:14 UTC (`97096452`, `162bd812`, both "Deployment has completed"), after refusing three earlier in the day (session 205's report). Production therefore serves `162bd812`. The merge changes no file under `site/` against that commit (`git diff --name-only 162bd812 b582a777 -- site`: none), so every page is what this landing would serve. Why no deployment was started for the merge, I did not establish: there is no Vercel sign-in on this machine.

## Decisions made without you

- **Impeccable without its hooks.** Its plugin and its installer add three hooks that run its engine after every edit and at the end of every turn, in every session on the machine, and feed findings back to the model. Its own README says to review them before unattended runs. I installed the skill with `--no-hooks`; the command to add them is in ruling 1.
- **User level, not the repository.** "Install on this machine": nothing under this repository's `.claude/`, so no third party's files are committed and another machine is not changed by a pull.
- **Only the three skills named** from `anthropics/skills` and `vercel-labs/agent-skills`, not their whole sets (19 and 9 skills), through the `skills` command with its telemetry off.
- **chrome-devtools-mcp pinned to 1.10.1**, headless, a fresh profile each run, Google's usage statistics off and no request to its field-data service. `@latest` would fetch new code at every session start.
- **AccessLint from the marketplace you named** (`accesslint/claude-marketplace`); its own README now names `accesslint/skills`. Same plugin name.
- **The nested run.** UI/UX Pro Max is a plugin and loads only at a start, so its proof ran in a second Claude Code process (`claude -p`, hooks off, read tools and `python` only). Claude Code's own work, no API call.
- **Impeccable's critique used two agents**, as its playbook requires; its questions were not asked and its snapshot was not written into the repository.
- **The token.** The proof scripts read `INTERNAL_COSTS_TOKEN` from `site/.env.local`, put it in the unlock request and strip it from everything they write. I searched the run folders for it: not there.
- **The test no longer asserts "planner: off".** A test that fails when you turn the planner on would block every landing that day.
- **The roadmap's Status lines are your words**, not rewritten into the planner's format. The planner refuses them while off anyway; ruling 2.
- **The pause.** I counted the long end in working time. The session did not stop itself at 2:30 of wall clock, because nothing was running to stop.
- **The report lands with the work; the landing's result is added to it in session 202's branch**, as session 205 did for 204.

## For Samuel's ruling

1. Impeccable's hooks: yes or no. With them, every session on the old laptop gets design findings after each edit of a UI file and a "deep pass" before it ends its turn; an unattended session may act on them outside its task. To add: `npx impeccable install --providers=claude --scope=global` in a terminal on the old laptop.
2. The roadmap's budget line. The planner reads only "budget: N sessions a day per machine". Yours is "no limit on sessions; stop at the weekly Claude limit". Give a number, or rule that the planner learns "no limit".
3. The roadmap's deploy cutoff. The planner reads daily windows in UTC. Yours is "Sundays 15:30 to 16:45 Pacific". Either the planner learns weekdays, or the line becomes "22:30 to 23:45 UTC" every day (stricter than you asked).
4. The roadmap's ten items have no `machine:`, `where:` and `done:` lines, which the planner needs before it plans one. Who writes them: you at Wednesday's review, or a session drafts them for you to correct.
5. `CLAUDE.md` says three pages are live (`/cost-of-power/battery`, `/network`, `/storage`). None is, since session 166. Whether the paragraph "The live pages and the freeze" is corrected (a patch can be prepared).
6. The two patches of Part C: apply or not. Note on the second: the three allow rules match `python scripts/precheck.py`, and every chain runs `.venv\Scripts\python.exe scripts/precheck.py`, which they do not match. Whether to add that form too.
7. Whether the tools are installed on the lab desktop as well. Today a design task planned for that machine would find none.
8. The battery page, structure (outside session 203's restyle), from Impeccable: (a) one rule for when an input applies (today: Duration at once, Grid and Strategy on "Show", scenarios as typed); (b) a side panel that stays in view.
9. The battery page, accessibility that needs markup: a table of the year chart's values; an announcement when the headline changes; a distinct name for each of the ten "Reset" buttons.
10. The battery page, one unit rule for a column: "5.46 million" and "664,224" stand in the same column today.
11. Whether `PRODUCT.md` and `DESIGN.md` (Impeccable's context files, in the repository root) are wanted. It works without them and asks for them each run. `docs/brand.md` could be the one source and those two never written.
12. The pause from 09:15 to 16:40 UTC. I did not establish its cause (the weekly limit, or the laptop). Whether mail went out each 30 minutes while it lasted I did not check; session 202 reads that and changes it to one mail.

## The prompt

Chain of 12 October (night), sessions 201 to 203; this session's text: "Session 201: the roadmap in the repository, and the tools installed and proven. Long end 2:30. Branch task/201-tooling", Parts A, B and C, and "Done means: every install proven by its run; the roadmap and docs/tooling.md on main through a landing with snapshots (0 differences expected)."
