# Session 91 report: alerts

**Built, on `wip/091-alerts`, nothing deployed.** One line by email when a session waits for input or a permission, one line when a chain marked as running has saved nothing for 30 minutes, and a permission allowlist for the routine actions of a session. All three are documented in `docs/machines.md`, "Alerts". A test line reached your inbox at about 06:58 UTC ("ERW: a test of the alert path (session 91)"): that is the sender both alerts use.

## To make each live

```bash
# Nothing below was run. Vercel's preview of this branch (behind Vercel's login): https://erw-bwth7bxso-erw6.vercel.app

# 1. THE HOOK AND THE ALLOWLIST are one file, .claude/settings.json. They apply to a session started in a checkout
#    that holds this branch's copy of it. To have them on every machine, the branch goes to main. That is a push to
#    a task branch, which redeploys the site (no page changes), so the snapshots go around it:
git fetch origin && git checkout wip/091-alerts && git merge origin/main
python -m unittest tests.test_session91 tests.test_session90        # read its exit code
cd site && node scripts/snapshot-live.mjs take before-091 && cd ..
git push origin wip/091-alerts:task/091-alerts
# when the workflow has merged and Vercel has deployed:
cd site && node scripts/snapshot-live.mjs take after-091 && node scripts/snapshot-live.mjs compare before-091 after-091
#    (this branch carries session 90's 25-page snapshot script too, so one push lands both)
#    Then start a new session: a running session does not pick a new hook up.

# 2. THE CHAIN WATCH needs its workflow on main (step 1), then its place in the database's schedule:
python warehouse/supabase/apply.py --only 022                       # erw-chain-watch, every 15 minutes
python warehouse/supabase/scheduler.py --test chain-watch.yml       # one dispatch now; 204 = accepted
python warehouse/supabase/scheduler.py --status
#    Do not apply 022 before step 1: GitHub refuses a dispatch of a workflow main does not hold, every 15 minutes.

# 3. A CHAIN, from then on, starts and ends with:
python scripts/alert.py chain start --name "night of ..., sessions N to M" --hours 14
python scripts/alert.py chain done
#    Tonight's chain is marked (since 06:51 UTC, until 20:51 UTC) and I will mark it done at the end. Until step 2
#    nothing reads the mark, so tonight it alerts on nothing.

# 4. To silence the hook on a machine where you work at the keyboard:  an empty file .erw/alerts_off
```

**Read these four first:**

1. **I could not prove that Claude Code fires the hook, only that the hook does its part.** Starting a second session to watch it fire is a model call, and this chain allows none before session 92. What is proven: the settings file is valid; the command it names, run as written with a wait event on its input, exits 0 and prints nothing; the same code sent a real email. What rests on the documentation alone: that a wait raises a `Notification` of type `permission_prompt` or `idle_prompt`, and the names of the event's fields. The reference lists the types but its page, as I could fetch it, shows no example of the event; so the hook reads the type if it is there and otherwise reads the message. **The first time a session of yours waits after step 1, an email should arrive within about a minute. If none does, that is the thing to tell the next session.**
2. **At the keyboard the hook will write to you too.** "Waits for input" fires about a minute after Claude finishes and you have not typed. It is held to one email per session and kind every 10 minutes, and step 4 silences it per machine. I did not make it silent by default: you asked for the line whenever a session waits.
3. **The watch runs on GitHub, not on the laptop, and reads pushes.** The usual reason a chain stops saving is that its machine stopped, so the machine cannot be the one that notices. A save is a commit pushed to a `wip/` or `task/` branch, which every chain already does after each step, or a `chain beat`. The line comes once at 30 minutes and again every hour, not every 15 minutes.
4. **The allowlist cannot tell a wip push from the push that deploys.** `git push origin wip/x` is allowed; `git push origin wip/x:task/x` matches the same rule, because a `*` matches any text and an allow rule has no "except". I left it so and wrote it down, rather than add a rule that asks: an "ask" rule might also stop an unattended chain at the one deploy its prompt names, and I could not test that without risking this chain. Rules 8 and 9 of `CLAUDE.md` govern that push.

Energy Research Warehouse (ERW), session 91, on the old laptop (`samueloldlaptop`, data role), 2026-10-04 from 06:50 to about 07:10 UTC, unattended. **Model spend: USD 0.00.** No pull, no table, no model call, no force push, no deploy. The data lock was not taken. One row was written to `erw_locks`: the chain's mark, which is not the data lock. One test email was sent.

## What the documentation says, and what I did with it

Read: Claude Code's hooks reference and guide, and its permissions reference (`code.claude.com/docs/en/hooks`, `hooks-guide`, `permissions`, `permission-modes`).

| The documentation | What follows here |
|---|---|
| `Notification` fires "when Claude Code sends a notification"; its matcher filters the notification type; the types include `permission_prompt`, `idle_prompt`, `elicitation_dialog`, `agent_needs_input`, and others that are not waits (`auth_success`, `agent_completed`, the `quota_` ones) | Four matcher groups, one per kind of wait. A type that is not a wait sends nothing even if it reaches the script |
| A Notification hook cannot block: "Exit code and stderr are ignored" | The hook is for telling, and cannot hold a session. It is also `async`, with a 45-second timeout, prints nothing and always exits 0 |
| A command hook has a `shell` field, `bash` or `powershell`; the default is bash, or PowerShell on Windows without Git Bash; the default timeout is 600 seconds | `"shell": "bash"`, like the session-start hook already in the file |
| Hooks receive `session_id`, `cwd`, `transcript_path`, `hook_event_name` on standard input; `CLAUDE_PROJECT_DIR` is set | The line names the session and the folder; the command finds the script through `$CLAUDE_PROJECT_DIR` |
| Rules are evaluated "deny, then ask, then allow"; "rule specificity doesn't change the order" | A force push is in `deny`, so no allow rule or mode lets it through |
| "Put the `*` after the subcommand": `Bash(git *)` allows every git command | Every allow rule has at least two words before its first `*`; a test checks it |
| "A rule must match each subcommand independently" of a compound command | The rules are per command (`git add`, `git commit`), so `git add -A && git commit ...` passes when both do |
| An allow rule does not match past an assignment of an unknown variable | `ERW_LOCK_EXEMPT=1 python -m unittest` has its own rule |
| An output redirect's target is checked against `Edit` rules | `Edit(/runs/**)`: a gate's output goes to `runs/x.out` (rule 7) without a prompt |
| A Bash rule "isn't a security boundary": `git -C . push` is not matched by `Bash(git push *)` | The deny rules stop the usual spellings of a force push, and the document says they are a guard, not a wall |
| Project allow rules apply after the folder is trusted; deny rules always | Stated in the document |
| Permission rule changes apply to a running session from its next tool call; hooks are read at start | The deny rules already bind this session; the hook does not run in it |

## What was built

**`scripts/alert.py`**, standard library only, so a hook cannot fail for a missing package:

- `hook`: reads the event, builds the line, sends it. "A Claude Code session waits for a permission on samueloldlaptop (session f4e41419, in erw), in the chain "night of 4 October, sessions 90 to 101": Claude needs your permission to use Bash".
- `chain start | beat | done | status | check`: the mark and the check. "The chain "..." (samueloldlaptop/f4e41419) has saved nothing for 37 minutes: its last save was a push to wip/090-fixes at 06:48 UTC. Marked as running since 05:52 UTC."
- `send`: one line, now.

**The mark** is the row `chain` of `erw_locks`, through the data lock's own functions (migration 016): no new table and no migration to mark a chain. It lapses by itself; a mark that lapsed without `done` is said once.

**`.github/workflows/chain-watch.yml`**: every 15 minutes, read only (`contents: read`), under `warehouse/health.py` like every scheduled job, so it never fails on GitHub and its runs are in the daily health summary (`"chain watch": 96` runs a day expected). **Migration 022** adds it to the database's schedule. Not applied.

**`.claude/settings.json`**: the four hook groups; 68 new allow rules beside the 18 that were there (all kept), and 10 deny rules. Allowed: the git commands a session uses and a push to a `wip/` branch; the tests, the validator, the coverage builder, the lock, the derived builders, the archive, the Redivis draft uploader, sync and the email helpers; the site's build, type check, server and scripts; writes under `runs/`; fetches of the live site and GitHub. **Left out on purpose:** the connectors (a pull is approved per session), `apply.py` (a migration), anything that calls the model, and inline code (`python -c`, a heredoc), which can do anything and so is not a routine action. `defaultMode` is not set: the list reduces prompts, it does not choose how a chain runs.

## Tests and checks

| Check | Result |
|---|---|
| `tests/test_session91.py` | 25 tests pass, none sends or reaches a network. The line and its sender (one message per fixed recipient, nothing without a key, a refusal names no address). The hook: what it says for each kind, that only a wait is an alert, one email per session and kind every 10 minutes, a failed send does not silence the next, it never raises, and as a process it exits 0 and prints nothing on broken input. The check: quiet with no chain and after a save; one line at 30 minutes; said at 30, 90, 150, 210, 270 minutes and at no quarter between; a beat and the start count as saves; a lapsed mark is said once; the newest push is read from both kinds of branch. The settings: each kind of wait pipes to the script; the command runs as written; a force push is denied in seven spellings and an ordinary push is not; no allow rule has a wildcard before its subcommand, none names a connector, a migration, the model or inline code; every script the list names exists; the rules that were there are kept |
| The whole suite, here | 616 tests, exit 1: the one old failure (`test_session49`, known since session 82) |
| The settings file | valid JSON: 86 allow, 10 deny, 4 Notification groups, the session-start hook kept |
| The hook's command, run as the settings write it, silenced | exit 0, nothing printed |
| A real send | 1 fixed recipient, exit 0 |
| `chain start`, `status`, `check --dry-run` against the real database and GitHub | marked; the newest push read (07:00 UTC, `wip/091-alerts`); "quiet: saved 2 minutes ago" |
| On the runner | not run: no push to a task branch in this session |

Not run: the workflow itself (it is not on main), migration 022, and a session that waits (above).

## Errors and decisions

- **Decision: the watch reads pushes, not a heartbeat.** A heartbeat needs every session to remember it. A push is what "saved" means, and it is already the chain's rule.
- **Decision: once, then hourly.** Fifteen-minute repeats of the same line through a night would be the thing you turn off.
- **Decision: a force push is denied, though you asked for an allowlist.** It is the one rule every chain prompt repeats, and a deny rule costs nothing when nobody force pushes. Say so if you want it out: ten lines of the settings file.
- **Decision: no secrets rule.** A `Read` deny on `.env` would keep a session's file tools off the keys. I did not add it: it restricts, you did not ask for it, and a deny rule holds in every mode, so a mistake in it would stop a chain. Worth a thought.
- **Decision: the script uses the standard library only.** The first version imported `requests` and read `.env` through `python-dotenv`. A hook runs with whatever `python` the session's shell finds, which on this machine is not always the environment's (session 90's first load failed for exactly that).
- **Error, mine: the first version of the 10-minute limit noted an email before it was sent**, so a send that failed would have silenced the next try. A test with a refusing sender found it.
- **The documentation's own page for `Notification` shows no example event** in what I could fetch, so two field names (`message`, `notification_type`) are from the list of matcher values and the hooks guide, not from an example. The hook does not depend on either being present.

## For Samuel

1. **Tell the next session whether the first alert arrived** (read first, 1).
2. **The deploy push and the allowlist** (read first, 4). If you would rather be asked every time, the rule is `"ask": ["Bash(git push *:task/*)", "Bash(git push *:main)"]`; test it once at the keyboard with a session in the mode your chains run in, to see whether it holds an unattended chain.
3. **The mode your chains run in.** The allowlist matters only in a mode that asks. If chains run with prompts skipped, the deny rules still hold and the hook's "permission" line will rarely fire; the "input" line and the watch are then the two that matter.
