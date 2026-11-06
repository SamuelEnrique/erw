# Tooling: which tool a session uses for what

Energy Research Warehouse (ERW), session 201 (12 October 2026). Six design and browser tools are installed on the code machine (`samueloldlaptop`), at the user level of Claude Code, outside this repository. This page says when a session uses which. It is not `docs/tools.md` (the site's own tools for visitors) and not `docs/platform-tools.md` (the plan of record).

The proof run of each, on `/cost-of-power/battery`, is in session 201's report (`archive/sessions/SESSION_201_REPORT.md`).

## When a session uses which tool

One line each. "Page" means a page of `site/`, served from a local production build (`npm run build`, then `npx next start`), never `next dev`.

| The job | The tool | How |
|---|---|---|
| Design critique of a page, before and after a restyle | Impeccable | the skill `impeccable`, command `critique <page>`: a design review and a detector run in two separate agents, ten heuristics scored 0 to 4, priority issues P0 to P3 |
| A mechanical scan of changed UI files for known bad patterns | Impeccable | `~/.claude/skills/impeccable/scripts/impeccable detect --json <files>`: exit `0` clean, `2` findings |
| Looking up a pattern (a chart type, a form rule, a font pairing) while writing `docs/brand.md` or a component | UI/UX Pro Max | the plugin skill `ui-ux-pro-max`: its search script over a local database, no network |
| A new surface or a mockup with no direction yet | frontend-design | the skill `frontend-design`: one page of principles and the list of traits a generated page falls into; where the brand rules, the brand wins |
| Review of a page's code against interface rules (focus, forms, labels, links, tables) | web-design-guidelines | the skill `web-design-guidelines <files>`: findings as `file:line`; it reads its rules from GitHub at each use, which is a pull |
| Performance review of a page's React and Next.js code | react-best-practices | the skill `vercel-react-best-practices`: 70 rules by priority; read with the trace below, not instead of it |
| Browser check: what the page looks like and does at a width, its console, its requests, its load | chrome-devtools-mcp | the MCP server `chrome-devtools`: `navigate_page`, `take_screenshot`, `list_console_messages`, `list_network_requests`, `performance_start_trace`, `lighthouse_audit` |
| Accessibility of a rendered page, contrast included | AccessLint | the plugin `accesslint`: its MCP tool `audit_live <url>` (WCAG 2.2 A and AA; `include_aaa` for AAA, `wcag: ["1.4.3"]` for contrast alone), or its skills `accessibility-scan` and `accessibility-audit` |

## First use of each tool

Session 401 (21 October 2026; the roadmap's item 4: each tool "used in at least one session's checks"), read from the session reports. "First use" is the first session that ran the tool on a page of this site, all on the code machine; "On the five tool pages" is the first run on all of `/cost-of-power/battery`, `/cost-of-power/seller`, `/cost-of-power`, `/research` (once `/analysis`) and `/grid`, recorded in `docs/reviews/tooling-pass-2026-10-20.md`.

| Tool | First use | Where | On the five tool pages |
|---|---|---|---|
| Impeccable | 12 October 2026, session 201 | `/cost-of-power/battery`: `critique` and `detect` (`runs/session201/impeccable/`) | 21 October 2026, session 401: `detect` on the pages' files and on the shared components, `critique` as two separate agents, nothing written to `.impeccable/` |
| UI/UX Pro Max | 12 October 2026, session 201 | `/cost-of-power/battery`: 27 searches (`runs/session201/ui-ux-pro-max/`) | 21 October 2026, session 401: 12 searches of its guidelines, read against the rendered pages |
| frontend-design | 12 October 2026, session 201 | `/cost-of-power/battery`, against its principles (`runs/session201/frontend-design/critique.md`) | 21 October 2026, session 401 |
| web-design-guidelines | 12 October 2026, session 201 | the battery page's five files and two shared components, its rules fetched once and kept (`runs/session201/vercel-skills/guidelines_command.md`) | 21 October 2026, session 401, from the kept copy of the rules (no fetch) |
| react-best-practices | 12 October 2026, session 201 | the same files (`runs/session201/vercel-skills/react-best-practices.md`) | 21 October 2026, session 401 |
| chrome-devtools-mcp | 12 October 2026, session 201 | `/cost-of-power/battery`: 16 calls and the 390 px test (`runs/session201/chrome-devtools-mcp/`) | not by session 401: its shots and measurements were taken over the same DevTools protocol by `site/scripts/browser.mjs` (`docs/brand/review-401/shots-401.mjs`) |
| AccessLint | 12 October 2026, session 201 | `/cost-of-power/battery`: `audit_live`, AA and AAA (`runs/session201/accesslint/`) | 21 October 2026, session 401: `audit_live` on each page in the internal view, before and after the fixes |

Session 203 (12 October 2026) was the first to use Impeccable, UI/UX Pro Max, frontend-design and web-design-guidelines in a page change's own checks (the battery restyle). On lab-desktop each was installed and proven by session 207 (13 October 2026), chrome-devtools-mcp excepted.

**AccessLint on a page in review, without the token in an address** (session 401): start a headless browser on port 9222, open the internal view in it by the form (`unlockForm` of `site/scripts/browser.mjs`), and give `audit_live` the port; it reuses that browser and its cookie. Stop the browser when the audits are done.

## Order of use on a page change

1. Before: chrome-devtools-mcp screenshots at 1280 and 390 px, and every number read from the page's text.
2. While writing: the brand (`docs/brand.md`) rules; UI/UX Pro Max and frontend-design are for looking things up, not for deciding.
3. After, on a local production build: AccessLint `audit_live` (no new AA violation), chrome-devtools-mcp again (screenshots, console clean, layout shift not worse), Impeccable `detect` on the changed files, web-design-guidelines on the changed files.
4. For a restyle or a new page: Impeccable `critique`, its report kept under `runs/session<N>/`.
5. None of these is a gate of `CLAUDE.md`. The gates are the suite, the site build, the page's own check script and the snapshot.

## What every session must know about them

- **They are on both machines** (session 216, the owner's ruling of 12 October 2026). User level, on `samueloldlaptop` (the code machine, session 201) and on `lab-desktop` (the data machine, session 207): `~/.claude/skills/` (impeccable, frontend-design, web-design-guidelines, vercel-react-best-practices), two plugins (`ui-ux-pro-max@ui-ux-pro-max-skill`, `accesslint@accesslint`), one MCP server (`chrome-devtools`, in `~/.claude.json`). Nothing of them is in this repository; a third machine has none until the installs of session 201's report are repeated there. **chrome-devtools-mcp is proven on the old laptop only:** on lab-desktop the server exits at once in every form tried (session 207's report, step 3, and its ruling 3), so a browser check runs on the old laptop until a person proves it here.
- **A page in review answers the "in review" page.** Since session 166 no page is live, so a tool that opens a page as a visitor audits the curtain, not the page. Open the internal view first (`/internal/unlock` with `INTERNAL_COSTS_TOKEN` from `site/.env.local`) in the same browser, and never write the token into a file, a log or a report.
- **Impeccable asks questions and writes files by design.** Its playbooks end with questions to the user and tell the model to treat "the user is not watching" as untrue. In an unattended session the chain's rule holds: no question is asked, and the report says "Questions skipped". Its `init` and `document` commands write `PRODUCT.md` and `DESIGN.md` into the repository root, and `critique` can write `.impeccable/`: none of these is written without the owner's ruling. Its edit hooks (after every edit, and at the end of every turn) are not installed.
- **AccessLint leaves a browser running.** `audit_live` starts a headless Chrome on port 9222 with a temporary profile and does not stop it. Stop it when the audit is done (it holds the internal view's cookie).
- **chrome-devtools-mcp is pinned and quiet.** Version 1.10.1, headless, a fresh profile each run, usage statistics off, no request to Google's field-data service. Its `resize_page` cannot go below about 500 px in headless Chrome: for 390 px use `emulate` with a viewport.
- **chrome-devtools-mcp's `lighthouse_audit` leaves out performance and cannot score it** (session 411's finding, written here by session 428). The Lighthouse bundled in version 1.10.1 replaces every performance audit with a shim ("This audit was filtered out and is not available in this bundle"), so its performance score is 100 whatever the page does. A performance score comes from `site/scripts/lighthouse-pages.mjs` with Lighthouse 13.4.1 from npm in a folder outside the repository (`LIGHTHOUSE_DIR`), on a local build only; the runner refuses a report whose audits are shims.
- **Two of them fetch at use.** web-design-guidelines reads its rules from `raw.githubusercontent.com` each time; AccessLint's MCP server starts through `npx` and can download a newer version. In a session whose prompt says "Pulls: none", say so in the report or use the copy kept in `runs/session201/vercel-skills/guidelines_command.md`.
- **A tool's finding is a reading, not a ruling.** Pages recommend nothing; a change of words or structure a tool asks for goes under "For Samuel's ruling".
- **shadcn MCP and Bencium are not installed** (session 540, `docs/reviews/tooling-shadcn-bencium-2026-10-21.md`: evaluated, both "no", the installation Samuel's). UI/UX Pro Max's `ui-styling` skill tells a session to run `npx shadcn@latest init` and `add`: a session does not, since that writes a second theme beside `site/app/tokens.css` (round corners, a dark mode, animation). Its `shadcn_add.py` refuses while `site/components.json` does not exist; no session creates that file.
