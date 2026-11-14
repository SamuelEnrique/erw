# Sessions 6190 to 6219 report: the held-out set, a wrong sum found, and the key's limit (chain 283, samueloldlaptop)

14 November 2026, about 21:44 to 22:15 UTC. Chain file `queue/done/283-day-17-november-oldlaptop-ask-continued.md`, taken by name by chain 282's last step. Model: Fable, high effort. Branch `wip/6100-ask` (landing row 14 not landed), worktree `C:\Users\lossa\Documents\erw-6100`. Sessions 6190 to 6192 used.

## Read these first

- **Not meant, and yours to act on: the Anthropic API key reached its usage limit at about 21:55 UTC.** The API's words: "You have reached your specified API usage limits. You will regain access on 2026-12-01 at 00:00 UTC." It is the key in the repository's `.env`. Every asking stopped there. If the weekday Digest's scoring, the Sunday Roundup's analysis or `/ask` share that key or its workspace, they are refused too until you raise the limit in the Anthropic console. I could not check that from this machine and tried no other key.
- **The day's spend under the key was about USD 59**: window P3's USD 10.72 in the morning, and USD 48.17 by this machine's four chains (USD 19.32, 14.49, 12.65 and 1.71). Each chain stayed under its USD 20 and every session under USD 2, as your instruction set them; a cap that renews with every chain let the day's total run to the console's limit. I should have told you the running total at each chain's end.
- **The held-out set found a wrong number in the chat, of a kind no check of the loop could catch.** Asked how many MW are withdrawn in SPP's queue, the chat said 419,388.74 MW. The rows sum to 419,636.34. The figure was fetched and cited; the tool's read was wrong. Fixed in the site's tool and proved with no model.
- **Of the 24 held-out questions answered before the key stopped, 23 were right.** Ten were not asked.

## The held-out set (sessions 6191, 6192)

- **35 questions written after the fixes of chains 280 to 282, never asked before**: other hubs, days, months and tables than the platform set's; 17 figures, 4 holds, a pause, 3 not live, 4 outside, a gap, 5 windows held in part. Builder `scripts/ask_eval/heldout_questions.py`; every key computed from the live set with a visitor's key and committed (`0f01ca06e`) before the first asking.
- **Five candidates could not be keyed** (a window held in part, a month or a status with no row) and are named in `keys_heldout.json`. Three of them are asked as what they are, windows held in part, decided before any asking.

| Class | Asked before the key stopped: 25 of 35 |
|---|---:|
| correct | 16 |
| correctly refused | 7 |
| unsupported number | 0 |
| wrong | 1 (h19) |
| ended in the API's error | 1 (h30) |
| not asked | 10 (h31 to h40) |

- Estimate before: at most USD 2.00 a session, about USD 0.08 a question. Actual: USD 1.7086 for the 25 (the 25th's first call was paid before the refusal).
- **The ten not asked are the refusals for something outside the warehouse, the missing day and the five windows held in part.** They wait for the key.

## The wrong sum (h19), found and fixed with no model

- **What happened.** The site's query tool reads a table of things in pages of 1,000, in the order of the table's time column. The rows of a queue's snapshot share one status date, so that order is not whole: a page is cut anywhere among equal rows, and a read of three pages held one row twice and missed another. The count stayed 2,058; the sum moved by 247.6 MW. The same wrong figure came back on every asking.
- **Checked three ways:** the rows read directly with a visitor's key, in any order and by id: 2,058 distinct rows, 419,636.335 MW. The Python tool over the same live set (it reads the table whole): 419,636.335. The site's tool before the fix: 419,388.735, twice.
- **The fix** (`site/lib/chat/tools.ts`): the read is in the order of the time and then of the rows' own ids (`entity_id`, `event_id`; entity and variable for a series). The site's tool after it: 419,636.335. Five other reads asked before and after are unchanged (CAISO's withdrawn 382,686.67 MW over 1,765 rows; ERCOT's active 308,487.96 MW over 1,159; a day's mean price; a count; a week of prices by hub).
- **Who was exposed.** Any sum, mean or extreme over more than 1,000 rows of a table of things or events whose time column repeats, and any series read across entities over more than 1,000 rows. The stored answers that read such tables matched their keys (CAISO's 1,765 withdrawn rows among them), so no other wrong figure is known; none can be ruled out for a visitor's question nobody keyed.
- **Why no check caught it.** The number stood in a tool result, so the number check passed it, rightly. Only a key computed another way could show it, and only a question nobody had asked before did.
- Held by `tests/test_session6192_ask.py` (5 tests).

## Checks run (exit codes read, none piped)

- Every test file that names a changed module, the spec or a record, each in its own process: 87 files, all pass (`runs/s6192/sweep.out` and the rerun of one, `test_session1315`, after the new keys file was named in the list of runs).
- Both loops turn by turn: 25 scenarios, equal.
- No site build, no type check, no lint, no whole suite: this machine's rule.

## Pushes to main and their snapshots

- `9efc2293a` (the queue move, file 284): `s6190-before` (21:44 UTC, also the after of chain 282's last push) and `s6190-after` (21:50 UTC): 25 pages, 0 differences in each comparison (expected).
- The last push of this chain (this report, the note, row 14's move, file 284's list): its snapshots are in the chain's last message.

## Decisions made without you

- **No other key and no other route was tried** when the API refused. The limit is your setting.
- **The chain stops asking and does not take file 284.** What is left needs the model (the ten held-out questions, any check of a new mend), or the data machine, or your rulings. An empty chain would only fill the queue. File 284 holds the list for when the key answers again.
- **The paging fix was made without an asking to confirm it**: it is a read of rows, proved against the rows themselves.
- **A desktop notification was sent to you at 22:00 UTC** about the key, because the Sunday Roundup runs in a day and may need it.

## For Samuel's ruling (default in brackets)

- **The key's limit and the Roundup.** [you raise the limit in the console if the scheduled steps share the key; nothing here can]
- **A ceiling for a day's evaluation spend across chains.** [USD 20 a day in all, said in each chain file, until you say otherwise]
- **Whether the landing desk should take row 14 soon for the paging fix alone.** [yes: it is the one change of the stack that corrects a figure a visitor could be given today]
