# Chain template

Energy Research Warehouse (ERW), session 188. The shape of a prompt file for the chain queue (`queue/README.md`).
Copy everything below the line into `queue/next/NNN-<slug>.md`, fill in what stands in angle brackets, strike a rule
that does not apply, commit and push. The first rule and the last rule stay as they are: they are what keeps a machine
from waiting for a person. This file itself is never taken by the queue (its name is not `NNN-<slug>.md`).

---

# Chain of <day and month>: sessions <first> to <last>

<Which machine, which folder, unattended. The sessions in order. One line on why this chain, and for whom.>

## Rules for every session of this chain

Every python command of this chain names the repository's interpreter, `.venv\Scripts\python.exe` on Windows (`.venv/bin/python` elsewhere), where a rule below says `python`: the bare `python` is the machine's global one and may hold no package (session 198 found this; session 199).

1. **Precheck first.** Before anything else, each session runs `python scripts/precheck.py --what "session <N>"` and reads its exit code. Exit 0: the machine is on duty and the session starts. Exit 1: the precheck has written its report under `runs/precheck/` and recorded the machine as idle (its one email follows 15 minutes later and says why); the session stops there, starts no work and does not wait for a person.
2. **Unattended.** Do not stop to ask questions. Follow the rulings written here. Where this file is silent, choose the reversible option and say so in the report under "Decisions made without you".
3. **A failed session does not stop the chain.** A session that cannot finish records what it did and what failed in its report, leaves its work on a `wip/` branch pushed to GitHub, and the next session starts.
4. **Landing.** `python scripts/freeze.py status` before a push that deploys. A snapshot before and after every landing, each its own command, every difference listed and marked expected or not (`CLAUDE.md` rules 8 and 9). Never force push. If the daily run lands during a session, pull and merge it.
5. **Data writes go under the data lock.** A code machine writes no warehouse data.
6. **Pulls:** only the pulls approved in a session's part, under its ceiling. Before any new host, read its robots file and terms; if they forbid the request, send nothing and report it. No request to a paused publisher (`warehouse/metadata/paused_sources.csv`).
7. **Model spend:** each session's cap is in its part, checked before each call. Over the cap, stop the spending step and report. Total for the chain: USD <total>.
8. **A long step is a silence.** Before a build or a pull of more than half an hour, run `python scripts/duty.py beat`: a machine on duty that has run nothing for 30 minutes is recorded as silent in the health table (it is not emailed: `docs/machines.md`, "The email rule").
9. **Writing:** no em dashes anywhere (pages, reports, documents, commit messages).
10. **Reports:** `archive/sessions/SESSION_<N>_REPORT.md`, short bullet points, no prose paragraphs. "Read these first" (at most five bullets); "What to review" with the full address of each changed page and click-by-click steps; pulls and spend against their ceilings; checks run with their exit codes; the landing and its snapshot comparison; "Decisions made without you"; and what waits for the owner under the heading "For Samuel's ruling", one item a line, so that `/internal/waits` lists it.
11. <Any rule of this chain alone: a deploy cutoff, a folder not to touch, a page not to change.>
12. **Last step of the last session: the queue.** After its report is pushed, the chain's last session runs `python scripts/chain_queue.py next`. Exit 0: the last line printed is the path of the next prompt file, now in `queue/done/`; read that file and run it as this one was run, starting with its precheck. Exit 3: nothing waits; the command has recorded the machine as idle and taken it off duty, and the machine's one email, "ready for review", follows 15 minutes later from the chain watch; say "CHAIN DONE" and stop. With `planner: on` in `docs/roadmap.md` (it is off unless a person turned it on), the same command first runs `python scripts/planner.py draft`: a chain the planner writes is committed, pushed to a `wip/` branch and taken as the next file (exit 0, its path printed as above); when the planner refuses, the command idles as said (exit 3).

---

## Session <N>: <what it builds, in a line>

Long end <hours:minutes>. Model spend cap USD <cap>. Pulls: <none, or each approved pull with its ceiling>.

- <What to build, in the owner's words. Rulings the session needs. What must not change.>
- <What "done" is: the checks that must pass, what the report must show.>

## Session <N+1>: <what it builds, in a line>

Long end <hours:minutes>. Model spend cap USD <cap>. Pulls: <none>.

- <...>
