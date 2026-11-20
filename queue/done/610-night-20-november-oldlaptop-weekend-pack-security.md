# Chain of 20 November 2026, night: sessions 9400 to 9599, samueloldlaptop (code role), one session, unattended, until the weekly limit: everything that waits for Samuel in one weekend pack, then the security review of everything the site gained this month

machine: samueloldlaptop

Written by Claude in chat with Samuel on 20 November 2026 at about 02:10 PST and uploaded by him to `queue/next`. It is not a machine's successor file, and no machine writes a successor to it. Folder: `C:\Users\lossa\Documents\erw`. Model: Opus 5.5. Run it unattended, to its last session. Do not stop to ask questions. Model spend USD 0: call no model API. No heredocs or long inline scripts: use the Edit and Write tools, and put scripts in `runs/`.

## Why this chain

Samuel could not review this week and has set the weekend aside for it. Since 10 November the machines have written a great deal that waits for him: rulings in the notes of a dozen chains, 40 findings for his Stata run, signature packs, license questions, and more than twenty new pages and views he has never opened. The page written for his hour on 19 November (`docs/reviews/tonight-2026-11-19.md`) covered part of it. Part A makes the weekend's pack: one place, in the order that frees the most work per minute of his time. Then part B. The site is private today and is meant to open. In the last month it gained dozens of routes, an approval control, a game that writes plays, a chat with a spending guard, and internal pages behind a cookie. Nobody has read all of that as an attacker would. Opening a site with a hole in it would cost Samuel more than any feature would earn him.

## Rules

- **The rules of chain 590 hold word for word** (`queue/done/590-evening-19-november-oldlaptop-tonight-pack-switches-ready.md`, and through it chain 507 and the owner's rules of 16 November as `queue/done/302-day-16-november-oldlaptop-large-load-on-the-site.md` has them), with these changes:
- **Session numbers** 9400 to 9599, each checked free on origin/main and every branch first.
- **This machine is short of memory:** no site build, no hourly table rebuilt, no timer or sleep that waits. A thing not ready is skipped and returned to.
- **No ruling is taken for Samuel.** No default on main changes. No `wip/alt-*` or `wip/switch-*` branch is landed or requested for landing.
- **The rule against a session whose only output is a record does not apply to part A.**
- **The security review attacks nothing that is live.** No request is sent to the production site, to Supabase, to Vercel or to any other service beyond an ordinary page read with the internal cookie. Every finding is shown by reading the code and by a test that runs against the code on this machine. No secret is printed, copied into a file or committed: a secret found where it should not be is named by its variable and its file, and nothing more.
- **A security finding of high severity is not written in a public place.** The repository is public. Such a finding is fixed on a branch whose commit message says only "hardening", its landing is requested at once, and the finding itself is written only after the fix has landed. Until then the report says "one finding held back until its fix lands", with no detail.
- **The words of `/privacy` and `/terms` are Samuel's.** Part C lists where they and the code disagree and changes neither.
- **Plain words, full addresses, no codes without their meaning, no em dashes.**
- **Never end idle.** After part D, part E, until the weekly limit.

## Restart safety and the progress file

- The first session writes `queue/next/611-resume-chain-610.md`, committed alone and pushed. Its text is the lines between BEGIN and END below, without those two words. A session that takes a resume file first writes the same text under the next number up (to 619), its machine line unchanged. The chain's last session removes it.
- `docs/state/progress_c610.md`: one line a step, its state and session, pushed after each.

BEGIN
# Resume of chain 610

machine: samueloldlaptop

Chain 610 was interrupted. This file is the old laptop's: another machine leaves it where it is. First put this same text back in queue/next/ as the next number up to 619, named NNN-resume-chain-610.md, committed alone and pushed. Then read queue/done/610-night-20-november-oldlaptop-weekend-pack-security.md whole and docs/state/progress_c610.md, and continue chain 610 from the first step not marked done, under that file's rules, with the next free session number in its range. Write no other queue file.
END

## Part A: the weekend pack, `docs/reviews/weekend-2026-11-21.md` on main (done and pushed within this chain's first two hours)

1. **What is read:** every note under `docs/state/` since 10 November and every chain's "For Samuel's ruling", "Decisions made without you" and "Needs the key"; `docs/reviews/rulings-one-sitting-2026-11-19.md` and the ranked and defaults lists; `docs/reviews/switch-ready-2026-11-19.md`; the sheet of forty findings and `docs/findings/_top40/`; the signature packs; `docs/licenses.md` and every license question a note raises; `docs/reviews/tonight-2026-11-19.md`. A question asked in three notes is one line with its three sources.
2. **The pack, in this order, each part with the minutes it takes:**
   - **If you have thirty minutes:** the ten decisions that free the most machine work, each in three lines with its two choices and what follows from each.
   - **Rulings that move a figure:** the groups of the one-sitting sheet, each ruled by one line; then his own twelve; then one "defaults stand". For each group, the branch that is ready to land the minute he rules.
   - **Rulings from this week's building:** by page, one line each with the default the machine took: where a new page sits in the menu, a source not pulled, a column that means two things, and the like.
   - **Findings:** how to run `run_top10.do` and `run_top40.do`, what they print, and how to approve at `/internal/findings`.
   - **Signatures:** each method note that waits for his signature, with its do-file, one line a tool.
   - **Licenses and money:** each publisher whose permission is needed, what is held back until it comes, and what it costs where a price is known; each step that needs the key, with its cost in US dollars and the sum.
   - **What was built, to look at:** every page and view landed since 17 November, by its full address (`https://erw-flame.vercel.app/...`), with what to click, step by step, and what he should see. Each address checked against main before it is written.
   - **The words to paste:** a template with blanks that he can fill and paste to Claude in chat to rule on everything above in one message.
3. Short bullets throughout. No line he would have to read twice. The first line says when it was written.

## Part B: the security review (`docs/security.md` is the last review; this one covers everything since, and anything that review left open)

1. **The ground:** every route handler and every page that reads a request (under `site/app/`, the `api` routes and the `internal` pages among them), `site/proxy.ts`, `site/lib/guard.ts`, the cookie and session code, every place a request's input reaches Supabase, a file path, a shell, a redirect or the page as markup; every place the site writes (the game's plays, the findings' approval and state, subscriptions, feedback); the chat's routes and its spending guard; the headers the site sends; the workflows under `.github/workflows/` and what secrets they can read. Listed in `docs/reviews/security-ground-2026-11-20.md`, by route, with what each trusts.
2. **Each route read as an attacker would:** who may call it and is that checked on the server; can the internal cookie be forged, replayed or skipped; can a visitor read what is held or internal (the held grids' figures, an internal table, a draft finding); can a write be made without a right to it, or made many times; can an input change a query, a path or the markup; can a request spend money (a model call, a large query) without a ceiling; does an error give away more than it should.
3. **Each finding:** its severity (high, medium, low), a test that shows it against the code, the fix with that test passing, on a branch, landing requested. High severity as the rule above says. A finding whose fix is a choice (a rate limit's size, whether a page should be internal) is fixed at the safer choice and written as one plain line for Samuel's ruling.
4. **Dependencies:** the advisories that apply to the versions the site and the Python code pin, read from the lock files and the public advisory lists; an upgrade that is a patch release and passes the tests goes on a branch; anything larger is listed.
5. **The repository's history:** a search by pattern for anything that looks like a key or a token in any commit; a hit is named by file and commit, never printed, and written at the top of the note for Samuel to rotate.
6. `docs/security.md` brought up to date: what was reviewed, what was fixed, what stands open and why.

## Part C: what the site says it does and what it does

`/privacy` and `/terms` read against the code: every cookie the site sets, everything it stores about a visitor (an email, a game's plays, a question typed into the chat, feedback, an address in a log), everything it sends to another service. Where the pages and the code disagree, one row: what the page says, what the code does, where. Written to `docs/reviews/privacy-against-code-2026-11-20.md`. Nothing changed.

## Part D: what a browser would complain of, found without one

- Every internal link and every address a page prints, checked against the routes that exist.
- Every image and chart without a text alternative, every control without a name a screen reader can say, every heading that skips a level, every pair of text and background colors below the contrast the brand file asks for: found by reading the components, fixed with a test, landing requested page by page.

## Part E: after part D, until the weekly limit

- Part A brought up to date whenever another machine's note adds a ruling or a landed page, until Saturday 10:00 PST; the time on its first line changed each time.
- Part B again for any route landed since its ground was written.
- The pages with the fewest tests: for each, the tests that pin what a reader sees.

## The last session

- `docs/state/note_2026-11-20_oldlaptop_c610.md` in short bullets: where the weekend pack is and how many minutes it asks; the security review's counts by severity, fixed and open, with nothing of a held-back finding; what part C found; what waits for Samuel, in plain words.
- The resume file removed; `.venv\Scripts\python.exe scripts\chain_queue.py next`, and the file it prints run the same way. No file: part E goes on.
