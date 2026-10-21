# shadcn MCP and Bencium, evaluated: nothing installed

Energy Research Warehouse (ERW), session 540 (21 October 2026, chain 024, unattended, on the code machine `samueloldlaptop`). The roadmap's item 4, "Tooling" (`docs/roadmap.md`): "shadcn MCP and Bencium evaluated in a written note under docs/reviews/". Session 201 gave each a paragraph on 12 October (`archive/sessions/SESSION_201_REPORT.md`, "shadcn MCP: no, for now" and "Bencium UX designer: no; its design audit, later"); this note reads both again from their public pages, against `docs/brand.md` and `docs/tooling.md`.

Nothing was installed, no MCP server was added, no settings file was edited and no package was downloaded. The installation, if any, is Samuel's.

## The two answers

- **shadcn MCP: do not install.** It is a search and copy service for components built on Radix and Tailwind, and it only works once `shadcn init` has put a second theme (round corners, a dark mode, animation, OKLCH colors) beside `site/app/tokens.css`. The site has none of the widgets it is for. If a widget hard to write well by hand is ever needed (a combobox, a dialog), read that one component's source from the public registry, under its MIT license, and write it on the tokens: no CLI, no `components.json`, no MCP server.
- **Bencium: install none of its nineteen plugins.** The controlled designer asks before every decision, the typography plugin silently writes em dashes and curly quotes and forbids the underlined link the brand requires, and the design audit reads and writes files the ERW does not keep. The audit's fifteen dimensions are a useful checklist; a session can read them from this note without the plugin.

## What was read

Twenty-four requests, all by `curl` from the code machine, each with the ruled contact string as its user agent ("ERW research project, github.com/SamuelEnrique/erw") and no address of any person; one second between requests (GitHub's robots file asks a crawl delay of 1). The files are kept in `runs/chain_024/s540/fetched/` on the code machine (not in git).

| # | Address | Status | Why |
|---|---|---|---|
| 1 | `https://ui.shadcn.com/robots.txt` | 200 | robots first: `User-Agent: *`, `Allow: /` |
| 2 | `https://github.com/robots.txt` | 200 | robots first: repository pages and `/blob/` allowed; `/tree/`, `/raw/`, `/archive/` and the commit lists disallowed |
| 3 | `https://raw.githubusercontent.com/robots.txt` | 404 | robots first: the host has none, so nothing is disallowed; files were read here, pinned to a commit |
| 4 | `https://ui.shadcn.com/docs/mcp` | 200 | the MCP server's documentation |
| 5 | `https://ui.shadcn.com/llms.txt` | 200 | shadcn's own summary and index of its documentation |
| 6 | `https://raw.githubusercontent.com/shadcn-ui/ui/main/packages/shadcn/src/mcp/index.ts` | 200 | the server's source: its seven tools |
| 7 | `https://raw.githubusercontent.com/shadcn-ui/ui/main/LICENSE.md` | 200 | the license: MIT, "Copyright (c) 2023 shadcn" |
| 8 | `https://ui.shadcn.com/docs/skills` | 200 | shadcn's Claude Code skill, which the MCP page points to |
| 9 | `https://raw.githubusercontent.com/shadcn-ui/ui/main/packages/shadcn/src/mcp/utils.ts` | 200 | whether the "add" tool runs the command or only writes it |
| 10 | `https://ui.shadcn.com/docs/installation/next` | 200 | what setting it up in a Next.js project does |
| 11 | `https://registry.npmjs.org/shadcn/latest` | 200 | the published version's metadata (version, license, dependencies); the package itself was not downloaded |
| 12 | `https://ui.shadcn.com/docs/installation/manual` | 200 | the files and dependencies a setup adds, written out |
| 13 | `https://github.com/bencium/bencium-marketplace` | 200 | the repository page: its commit |
| 14 | `https://raw.githubusercontent.com/bencium/bencium-marketplace/main/README.md` | 200 | the marketplace's README |
| 15 | `https://raw.githubusercontent.com/bencium/bencium-marketplace/main/.claude-plugin/marketplace.json` | 200 | the list of plugins with their versions |
| 16 | `.../bencium-marketplace/5de46a39.../LICENSE` (raw, at the commit) | 200 | the license: MIT, "Copyright (c) 2026 bencium.io" |
| 17 | `.../5de46a39.../design-audit/skills/design-audit/SKILL.md` | 200 | the design audit, read whole |
| 18 | `.../5de46a39.../typography/skills/typography/SKILL.md` | 200 | the typography plugin, read whole |
| 19 | `.../5de46a39.../bencium-controlled-ux-designer/skills/bencium-controlled-ux-designer/SKILL.md` | 200 | the controlled designer |
| 20 | `https://ui.shadcn.com/sitemap.xml` | 200 | terms: 405 addresses, none named terms, legal, privacy or license |
| 21 | `https://docs.github.com/robots.txt` | 200 | robots first: `User-agent: *` and nothing disallowed |
| 22 | `.../5de46a39.../typography/.claude-plugin/plugin.json` | 200 | whether the typography plugin carries a hook (it does not: a name, a version and a description) |
| 23 | `https://docs.github.com/en/site-policy/github-terms/github-terms-of-service` | 200 | GitHub's terms (effective 27 April 2026): nothing in them stops reading a few public pages by hand; the clauses on automated access concern accounts, training AI systems and API abuse |
| 24 | `https://registry.npmjs.org/robots.txt` | 200 | robots, read late (after request 11, found by this session's test): the registry has no robots file; the address answers the metadata of an npm package named `robots.txt`. The registry is npm's public package API, read once for one version's metadata |

The commit `5de46a39b4640fa419560cd0b67e4c4b50dac802` is the one the repository page named tonight (`currentOid`), the same commit session 201 read on 12 October: the marketplace has not moved since. One request was out of order: npm's registry (request 11) was read before its robots address (request 24), which holds no robots file; the order is the rule, and it was missed once. The Bencium plugins' own website (`bencium.io`) was not read: the plugins' license is in the repository. Local reads, no network: `site/package.json`, `site/AGENTS.md`, `site/app/tokens.css`, a count of the site's widgets, and the installed UI/UX Pro Max plugin's `ui-styling` skill (`~/.claude/plugins/cache/ui-ux-pro-max-skill/ui-ux-pro-max/2.13.0/.claude/skills/ui-styling/`).

## shadcn MCP

### What it does

The MCP server is part of the `shadcn` command-line tool (npm `shadcn` 4.22.1 tonight, MIT; session 201 saw 4.21.4). Its documentation starts it with `npx shadcn@latest mcp`, or writes the entry for you with `shadcn@latest mcp init --client claude`. The server (request 6) has seven tools:

| Tool | What it returns |
|---|---|
| `get_project_registries` | the registries named in the project's `components.json`; an error where there is none |
| `list_items_in_registries` | the components, blocks and templates of those registries |
| `search_items_in_registries` | a fuzzy search over them |
| `view_items_in_registries` | an item's description and the full source of its files |
| `get_item_examples_from_registries` | example code ("accordion-demo") with its dependencies |
| `get_add_command_for_items` | the text of a command, such as `npx shadcn@latest add button` (request 9: `npxShadcn` builds a string; the server does not run it) |
| `get_audit_checklist` | six fixed lines: imports, `next/image` patterns, dependencies, lint, TypeScript, "Use the Playwright MCP if available" |

So the server reads and answers; the writing is done afterwards by the model, which runs the `add` command it was handed. Every tool but the checklist needs a `components.json` in the project.

shadcn also publishes a Claude Code skill (request 8, `skills add shadcn/ui`) that runs `shadcn info --json` "on every interaction" once a `components.json` exists, and tells the model to follow shadcn's composition rules ("using FieldGroup for forms, ToggleGroup for option sets, semantic colors").

### What it would read and write on this machine

- **Configuration.** The documented setup for Claude Code is a `.mcp.json` in the project's root, a file the repository does not have and that `docs/tooling.md` keeps outside it (the seven tools are user level). Writing one is a settings change, Samuel's.
- **Every start is a pull of the newest version.** `npx shadcn@latest` resolves `latest` from npm at each start, as AccessLint's server does (`docs/tooling.md`, "Two of them fetch at use"); nothing is pinned unless a person pins it.
- **Its first step writes the site's styling.** `shadcn init`, or the manual setup (request 12), adds `shadcn`, `class-variance-authority`, `cn`, `lucide-react` and `tw-animate-css` to `site/package.json`; writes `components.json` and `lib/utils.ts`; and puts a theme into the CSS: `@import "tw-animate-css"`, `--radius: 0.625rem` with seven radius steps, its colors as OKLCH values in `:root`, and a `.dark` block. The CLI command "follows the prompts" (request 10): it asks questions where it is run.
- **Network at use.** Each tool call reads the registries; the default registry is `https://ui.shadcn.com/r` (the package's `start:prod` script, request 11), and a third-party registry is any address a `components.json` names.
- **Secrets.** Private registries take tokens from the environment, and the documentation tells a user to put them in `.env.local` (request 4); the package depends on `@dotenvx/dotenvx` (request 11). I did not read the code that loads the file. `site/.env.local` holds the internal view's token: a tool that reads environment files in `site/` is one more reason to keep it out of there.

### Under the ERW's rules

- **One token file.** `site/AGENTS.md`: "Design tokens: `app/tokens.css` only." A shadcn setup adds a second set of colors and radii, written for its components to read, beside the brand's.
- **The brand says no to its defaults** (`docs/brand.md`): "Corners are square" (shadcn: 0.625rem); "No motion" (`tw-animate-css`); "Dark mode. None is proposed" (a `.dark` block); and "No shadow". Each default would be undone by hand, in each copied file.
- **The site does not need what it offers.** Counted tonight under `site/app` and `site/components`: 32 files hold a native `<select>`, 30 a `<details>`, one a `role="dialog"` (the battery game, `site/app/play/battery/Game.tsx`), none a combobox, a tab list or a popover. No Radix, no `lucide-react`, no `components.json` (`site/package.json`).
- **Unattended.** The MCP server asks nothing and writes no `PRODUCT.md` or `DESIGN.md`. The setup it depends on asks questions; an unattended session would stall on them or take the defaults, and the defaults are the ones above.
- **Already within reach.** The installed UI/UX Pro Max plugin carries a `ui-styling` skill that tells the model to run `npx shadcn@latest init` and `npx shadcn@latest add button card dialog form`, and a script, `shadcn_add.py`, that runs `npx shadcn@<version> add`. The script refuses to run without a `components.json` ("shadcn not initialized. Run 'npx shadcn@latest init' first"). Today the absence of `site/components.json` is the only thing between a session that follows that skill and a second styling system.

### Recommendation

Do not install the shadcn MCP server or its skill. When a page needs a widget that is costly to write well by hand, a session reads that one component's source (request 6's `view_items_in_registries` returns the same files the public registry serves), cites it, and writes it in `site/components/` on `tokens.css`: no CLI, no `components.json`, no new dependency without its own ruling.

## Bencium

### What it is

`github.com/bencium/bencium-marketplace` is a Claude Code plugin marketplace by bencium.io, MIT. Its `marketplace.json` lists nineteen plugins (the README says seventeen skills): six for design (the controlled, innovative and impact designers, `design-audit`, `typography`, `relationship-design`), and others for writing, architecture, marketing, an EU AI Act review, a statusline and a build loop. It installs either with `/plugin marketplace add bencium/bencium-marketplace` then `/plugin install`, or with `npx skills add bencium/bencium-marketplace -g`.

### What it would read and write on this machine

- **User-level Claude Code configuration.** A marketplace and its plugins are recorded in `~/.claude/plugins/` and enabled in the user's settings; `npx skills add -g` writes into the user's skills. Both are settings changes, Samuel's. The README's "spinner verbs" are pasted into `~/.claude/settings.json` by hand.
- **One plugin calls a model on its own.** `emotion-statusline` is a hook and a statusline, "Haiku-scored" in its description: a model call outside the chain's ledger, against the chains' rule of model spend USD 0.
- **The design audit reads and writes files at the project's root.** Before it starts it reads `DESIGN_SYSTEM.md`, `FRONTEND_GUIDELINES.md`, `APP_FLOW.md`, `PRD.md`, `TECH_STACK.md`, `progress.txt` and `LESSONS.md` (request 17); after an implementation it updates `progress.txt` and `LESSONS.md`. The ERW keeps none of these: `docs/brand.md` is the one design document, and the owner's ruling of 12 October (session 209) keeps `PRODUCT.md` and `DESIGN.md` out; the same holds for their kin.

### The four design plugins against the ERW's rules

- **Controlled UX designer** (1.0.0): its first rule is "ALWAYS ASK before making any design decisions (colors, fonts, sizes, layouts)" (request 19, line 15). An unattended session asks nothing (`docs/tooling.md`), and the decisions it would ask about are made in `docs/brand.md`. No.
- **Innovative UX designer** (3.1.5): ten typography-led directions for a person to lock (request 15). The direction is ruled (brand direction A, 12 October). Not read again tonight: the commit is the one session 201 read. No.
- **Typography** (1.0.0): its description says to "auto-apply every rule in this skill silently", "do not ask, do not explain", on any HTML, CSS, React or JSX it writes, whether or not typography was mentioned (request 18). Its rules contradict the ERW's in three places: the em dash for "sentence breaks" (`CLAUDE.md`, non-negotiable 2: no em dashes); "Never underline in a document or UI" (`docs/brand.md`: "A link in running text is underlined", the one finding every scanner of session 201 reported); all capitals "ALWAYS" letterspaced (`docs/brand.md`: "No capitals by style, no letter-spacing"). Its own file holds 46 em dashes and 16 en dashes. It carries no hook (request 22): the harm is in the skill's text, loaded on every page session. No, firmly.
- **Design audit** (1.0.0): a visual audit over fifteen dimensions, sorted into three phases, then "Wait for Approval ... Do not implement anything" (request 17). The waiting suits an unattended session; the files it reads and writes, above, do not, and its third phase asks for transitions, micro-interactions and a dark mode the brand excludes. Its file holds 19 em dashes, so text copied from it would carry them. It overlaps Impeccable's `critique`, which the ERW runs as two separate agents with nothing written to `.impeccable/`. No install; its dimensions are worth keeping as a checklist (below).

### The audit's dimensions, as a checklist

For a session that wants a second reading beside Impeccable's, read by hand, nothing installed: visual hierarchy, spacing and rhythm, typography, color, alignment and grid, components (every state: hover, focus, disabled), iconography, motion (the brand: none), empty states, loading states, error states, dark mode (the brand: none), density ("Can this be removed without losing meaning?"), responsiveness (touch targets), accessibility. Its findings go under "For Samuel's ruling", as every tool's do.

### Recommendation

Install none of the nineteen. Session 201's "its design audit, later" is answered: the audit is read once here, and its checklist is enough.

## What would change this

- **shadcn**: a page whose widget Radix does well and a hand-written one does badly (a searchable combobox over hundreds of entities, a modal with focus trapping), and Samuel's ruling to take one component's source. Even then, the copy-by-hand route above serves without the server.
- **Bencium**: a version of the typography plugin without the em dash, the curly quotes and the rule against underlined links; or of the design audit that reads one named design file (`docs/brand.md`) and writes nothing. Neither exists at commit `5de46a39`.

## For Samuel's ruling

- Install the shadcn MCP server: this note recommends no.
- Install any Bencium plugin: this note recommends no, typography above all.
- UI/UX Pro Max's `ui-styling` skill tells a session to run `npx shadcn@latest init`: whether to turn that one skill off at the user level (a settings change, yours), or leave it as is with `docs/tooling.md`'s new line as the guard.
