# Session 5151 report: row 6, the site's writes and the service key on the host: what a read can prove

13 November 2026, unattended, `portable-laptop` window P2. Branch `wip/5150-security`, worktree `erw-p2-5150`. Model spend USD 0. Pulls: two read-only transactions on the database (the catalog and counts; no address, no email, no visitor key printed or kept), one snapshot of the live pages. Nothing built, nothing landed, no warehouse data written, nothing asked of production but the snapshot.

Clock: precheck 18:48 UTC, the reads at 18:50 UTC, the tests at 18:52 UTC. Inside the long end of 1:00.

## Read these first

- **A read cannot prove it alone, and the look is now easier.** A row in the database does not say which server wrote it: a local build with the same `.env` writes the same tables.
- **What makes the look easy.** The question counter fails closed. Without `SUPABASE_SERVICE_KEY` on a server, the database refuses `site_ask_admit` (migration 034) and the route answers no question. So **one answered question on production's Ask says the key is there.**
- **What the database holds** (read at 18:50 UTC):
  - Migration 034 is in force: the anon key holds no insert on `site_api_calls`, `game_plays`, `game_scores`, `subscribers`, and cannot execute `site_ask_admit`.
  - Since 21 October, in the tables only the write key fills: 24 `site_ask` ledger rows and one counted visitor (3 questions), all on 6 November 2026; 2 game plays, the newest on 28 October; no sign-up, no score.
  - That one visitor's key is not the key of a local address (`::1`, `127.0.0.1`, none) under this machine's salt. That fits Vercel. It also fits a local build on a machine with another salt, so it is not written as proof.
- Row 6's state is now **ruling**, with the default "one question on production". Ruling 1.

## What to review

1. `docs/reviews/security-faults-2026-11-13.md`, row 6.
2. `docs/security.md`, the paragraph "Item 3 above (H3, the one look)".
3. `tests/test_session5151.py`: 5 tests, the three lines the look rests on.

## What was done

- **The catalog** (`runs/s5151/schema.py`): the policies and grants of the seven tables the site writes, and the anon key's right to execute each `site_` function. `site_ask_admit`: no. `site_rate_admit`, `site_usage_record`: yes (they ask for the internal token instead).
- **The counts** (`runs/s5151/writes.py`): rows since 21 October by table and day; the visitors of `site_ask_counts` sorted into local and other by computing the local addresses' keys here (the salt never printed).
- **The code read**: `rpc(..., { privileged: true })` goes with `writeConfig()`; `admit()` in `site/lib/chat/limits.ts` returns a refusal when the call throws and admits only on the database's own yes.
- **The test** pins those lines and the migration's revoke, so the look stays a proof.
- **The old worktree `erw-p2-5100` is removed** (its branch landed; its nine files equal commit `f3b56583c`, checked file by file). Its `runs/` folders (4,159 files, 33 MB: sessions 5100 to 5102's outputs and chain 234's snapshots) are copied to `erw-p2-5150\runs\from-erw-p2-5100\`. Session 5100's report names the old path: the outputs are at the new one.
- **Rule 8, once more for session 5150's push**: `s5151-after3` at 18:52 UTC, ten minutes after the push; `compare` against `s5150-before`: exit 0, 0 differences. Expected.

## Checks, with exit codes

| Command | Exit | Result |
|---|---|---|
| `scripts/precheck.py --what "session 5151 (window P2)"` | 0 | on duty |
| `git merge origin/main` | 0 | merged (`4181a63b5`) |
| `runs/s5151/schema.py`, `runs/s5151/writes.py` (read-only) | 0, 0 | as above |
| `pytest tests/test_session5151.py` with `5102`, `5101`, `371`, `1501` | 0 | 49 passed |
| `snapshot-live.mjs take s5151-after3`, `compare` | 0, 0 | 0 differences |

- **Not run:** the build, the whole suite, any request of production's Ask.
- **Not verified:** which server wrote the rows of 6 November.

## Decisions made without you

- **No question asked on production by this session.** It would spend under the owner's key on the host and needs the internal view opened there with the token; the chain leaves production to the snapshots.
- **No new route that prints the write key's role** (`writeRole()` exists and nothing calls it). An address behind the internal view would make the look a click; it is also a new page of the site, so it is a ruling, not done.
- **The test reads `site/lib/chat/limits.ts`**, a file of the Ask engine (window P3's), and changes nothing in it. If P3 rewrites `admit`, the test fails and says what the proof rested on.
- **`erw-p2-5100` removed, its outputs kept** by copy, since a report names them.

## For Samuel's ruling

1. Row 6, the look. Default: next time you are in the internal view on production, ask Ask one question; an answer closes the row. Or read Vercel's Environment Variables for `SUPABASE_SERVICE_KEY`.
2. An internal address that says which key the site's writes go with (`/internal/writes`, the internal view only, one word). Default: not built.

## The prompt

`queue/done/237-day-14-november-portable-p2-security-continued.md`, "Sessions 5151 to 5158: chain 234's unfinished steps", step 2 of the list session 5150 rebuilt.
