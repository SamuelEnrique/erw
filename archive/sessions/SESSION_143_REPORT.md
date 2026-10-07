# Session 143 report: Ask ERCOT, from 17 seconds toward 5

Run on 7 October 2026 (UTC), unattended, in the chain 140 to 145. An agent built it in a working copy of its own to a
written brief; I checked the suite, the landing and production myself. No page's face changed; nothing was loaded.

## Four things to know first

- **Both targets are missed.** A number question now takes **6.4 seconds to its words** at the median (it took 15 to
  17; the target is 5; 11 of 39 are under 5). An idea takes **2.3 seconds** (the target is 2; 2 of 20 are under 2).
- **"No loss on the 100" is shown on 78 questions, not 100.** The runner stopped before question 79 at USD 2.7055, as
  it must. Of the 78: 77 pass, and 77 of the same 78 passed in session 137's record. One gained (the year's highest
  hourly demand, which now answers 91,075 MW from the stress table), one lost (how batteries charge across the hours
  of a day: it answers with daily figures and no chart).
- **The 17 seconds were the model asking the same query again and again**, up to the limit of 8 calls. The cut that
  did most was not on your list: one reading turn, then one writing turn that can call no tool, and a query never
  made twice. Number questions went from 6.6 model calls to 2.8.
- **Today's site ledger stands at USD 2.82 of production's daily ceiling of 3**, so production would refuse almost
  every question until 00:00 UTC. It is closed anyway: `ASK_VISITOR_SALT` is still not set.

## Verdict: not ready to open on speed. What is left, exactly

1. **About 1.4 seconds more for number questions.** What remains is two model calls: a reading turn of about 2.7
   seconds, 0.2 seconds of reads, and 2.2 seconds of writing until the words. Candidates, none tested: lower effort on
   the reading turn; a plan made by rule for the commonest shapes of question.
2. **The slow tail is data.** One read of a year of hourly reserve prices took 13.3 seconds. A rollup of reserve
   prices by day or month needs a new table and a load, which tonight's freeze forbids; the derived script is not
   written.
3. **The 22 questions not asked and the one that failed**, about USD 0.45, after 00:00 UTC (commands under "To
   finish").
4. **Reading the pages of one large query together** means changing `site/lib/supabase.ts`, which the live pages
   share: not done in the freeze.
5. Still open from before: `ASK_VISITOR_SALT`, the provider's spending limit, the words on `/terms`; the Python
   reference loop knows none of this.

## Before and after, by stage

Seconds to what a reader sees, median (90th percentile). "Before" is two things: today's sample of 20 questions (5 of
each kind, with stages) and session 137's record for the same 78 questions (whole answer only).

| Kind | Before, today's sample: whole | Session 137, same 78: whole | After: first sign | After: words | After: whole |
|---|---|---|---|---|---|
| Conceptual (5 / 20) | 3.4 (7.7) | 3.4 (5.4) | 2.3 (3.1) | **2.3** (3.1) | 3.3 (4.3) |
| Chart (5 / 20) | 32.1 (33.5) | 13.4 (24.8) | 2.8 (3.7) | 6.3 (21.5) | 7.7 (21.5) |
| Sentence (5 / 19) | 9.8 (13.6) | 17.1 (24.6) | 3.2 (4.7) | 6.5 (15.0) | 7.2 (15.1) |
| Refuse (5 / 19) | 2.8 (3.5) | 3.0 (5.2) | 2.0 (3.1) | 2.1 (3.6) | 3.1 (4.2) |
| Number, both (10 / 39) | 16.4 (33.2) | 15.1 (24.8) | 2.8 (4.6) | **6.4** (17.5) | 7.5 (17.8) |

Stage medians in milliseconds, today's sample before and after:

| Kind | Planning | Fetching | Drawing | Writing | Other |
|---|---|---|---|---|---|
| Conceptual | 0, 0 | 0, 0 | 0, 0 | 3045, 3184 | 236, 159 |
| Chart | 17019, 2776 | 3530, 128 | 0, 0 | 4112, 3929 | 163, 152 |
| Sentence | 6008, 3525 | 91, 223 | 0, 0 | 3379, 3153 | 183, 142 |
| Refuse | 0, 0 | 0, 0 | 0, 0 | 2662, 2935 | 140, 141 |

- Number questions, means: planning 11.7 to 4.7 seconds; fetching 2.3 to 1.1; writing 4.5 to 4.4; total 18.7 to 10.4.
- Drawing never passes 1 millisecond. Admission (the ceilings and the visitor limit) is 91 ms before, 74 after.
- Today's chart sample is slower than session 137's because all five hit the limit of 8 calls. It is five questions.

## What each cut did, in your order

- **Cached table summaries:** each table's first and last date and the mix tables' variable names, from the catalogue,
  kept ten minutes. 1 millisecond at the median. It saves a model call and a read only where a question used to
  describe a table (2 of 10 in the sample).
- **Precomputed daily rollups: no table built** (none allowed tonight). Instead a grouped result carries its own low,
  high, first, last, change and mean, so a movement is one query. A real rollup is still wanted (verdict, item 2).
- **Parallel fetches: did little.** Calls of one turn already ran together since session 121; reads take 137 ms at
  the median.
- **A smaller model for planning: did nothing, and was not kept.** `claude-haiku-4-5` took 2.9 seconds for its first
  call against 2.8 for the Sonnet model on the same seven questions, called a tool for an idea question, and made 2 of
  7 answers twice. The models are unchanged: `claude-sonnet-5-5` for every call.
- **The sentence before the chart: 1.1 seconds earlier at the median**, on all 78. The words go out once their
  numbers, form and premise pass the check; nothing unchecked is shown.
- **Not on the list, and it did most:** one reading turn, one writing turn, no repeated query. 29 of 39 number answers
  are one read and one write (5.5 seconds to the words); the other 10 fell back to the old loop (8 to 44 seconds).
- **Also tried, not kept:** the model's lowest thinking setting (6 of 7 passed; no faster).

## Pass counts and cost, by the same judge

| Kind | Before, today's sample | After | Session 137, same questions | USD a question: today's sample before | Session 137, same 78 | After |
|---|---|---|---|---|---|---|
| Conceptual | 5 of 5 | 20 of 20 | 20 | 0.0155 | 0.0119 | 0.0105 |
| Chart | 5 of 5 | 19 of 20 | 20 | 0.0709 | 0.0466 | 0.0312 |
| Sentence | 4 of 5 | 19 of 19 | 18 | 0.0365 | 0.0449 | 0.0219 |
| Refuse | 5 of 5 | 19 of 19 | 19 | 0.0065 | 0.0070 | 0.0089 |
| **All** | 19 of 20 | **77 of 78** | 77 | 0.0323 | 0.0277 | **0.0182** |

- The same 78 questions cost USD 2.16 in session 137 and 1.42 now.
- 20 series shown, each equal to the rows fetched, none under a question that asked for no chart. No words were
  taken back after being shown.

## Every pull against its ceiling

- **No data pull. No MISO request, no PJM request. Nothing loaded into Supabase. No request to production's route.**

## Model spend: USD 2.7055 of the USD 3.00 cap (stop at 2.80)

| Run | Questions | USD | Planned before the first call |
|---|---|---|---|
| Before, today's sample (the tool as it stood) | 20 | 0.6467 | 0.60 |
| Probes (single questions, to see the tool calls) | 6 | 0.2322 | 0.40 for probes and trials |
| Trial: a smaller model plans | 7 | 0.1831 | |
| Trial: the lowest thinking setting | 7 | 0.2251 | |
| After, the same sample | 20 | 0.3509 | 0.30 |
| After, the rest (one of each kind in turn) | 58 | 1.0675 | 0.95 for 80 |
| **Total** | **118** | **2.7055** | 2.25 |

- **Refused before they started: 22 questions** (c20 c22 c23 c24 c25, h20 h22 h23 h24 h25, s19 s20 s22 s23 s24 s25,
  r19 r20 r22 r23 r24 r25). The runner stops before a question when the spend so far plus a reserve for one more
  would pass its stop. Nothing else was refused; no paid answer was discarded.
- The probes and trials ran USD 0.24 over their plan; that is what cost the last 22 questions.
- The site's own ledger agrees to the cent (285 calls, 118 questions). October stands at USD 10.03 of 30.
- The local server ran with a ceiling of its own; production's configured ceilings (3 a day, 30 a month, 15 questions
  a visitor a day) are unchanged.

## The landing

- **Freeze: on**, ending today; the chain's prompt names the landing. `/ask/ercot` and `/grid/ercot` stay `review`.
- The whole suite passed in a clean copy of the merged branch (1,692 tests). Checks passed (run 37612091429); merged
  as `709b07d`. It also carries sessions 140 and 141's reports to main.
- **Vercel built it:** "Deployment has completed" for `709b07d` at 11:17:39 UTC.
- **Snapshot before** (`143_before`, 11:08:25 UTC) **and after** (`143_after`, 11:17:49 UTC): **6 differences, all on
  `/network`, all its own hourly refresh at 11:05 UTC** (the refresh stamp, the newest demand hour from 08:00 to 09:00
  UTC, the source line's build stamp): expected, and not this deploy. **No checked number moved** (3,357 keys
  compared). Nothing was reverted.
- **On production, in the internal view, with recorded answers and no model call:** the panel's browser check passes
  13 of 13 and the new words-before-chart check 9 of 9.

## Checks

- `tests/test_session143.py` 17 tests; `site/scripts/test-ask-speed.mjs` 13 (recorded reads, no request): the stage
  timings sum to the whole; parallel reads return what serial ones returned; the summaries do not hide a newer day;
  the number check still refuses an unverified number; the ceilings are untouched.
- The earlier Ask tests (sessions 91, 92, 114, 121, 128, 137): passed. Browser checks with recorded answers: 13 of 13,
  9 of 9 and 23.
- One thing found: session 92's test of a grid page's chat reads `storage_capacity` with no guard, and errors on a
  machine that lacks that table.

## Decisions made without you

1. **A follow-up question that fails its check is dropped and the answer stands**; before, the whole answer was
   written again. No unverified number is shown. Say if you want the rewrite back.
2. A "not in the warehouse" or an empty answer from the fast writing turn is not trusted: the old loop takes over.
3. Every chat call, the general chat's too, is now read as a stream; the general chat is otherwise unchanged.
4. Four server switches for trials remain (`ASK_PLANNER`, `ASK_THINKING`, `ASK_FAST`, `ASK_WRITER_EFFORT`); unset is
   the design measured here.
5. As in session 137, 118 made-up addresses were counted in today's visitor table (it clears tomorrow).
6. Built in a working copy of its own, with its site builds taking turns with the other sessions' on this machine.

## To finish

```bash
# after 00:00 UTC, in site/ (about USD 0.45): the 22 questions not asked and the one that failed
npm run build
ASK_DAILY_USD=1 npx next start -p 3143
node scripts/eval-ask-speed.mjs http://localhost:3143 ../runs/session143/after_rest2.jsonl --run after_rest2 --spend ../runs/session143/spend2.json --stop 0.70 --reserve 0.10 --interleave --ids c20,c22,c23,c24,c25,h13,h20,h22,h23,h24,h25,s19,s20,s22,s23,s24,s25,r19,r20,r22,r23,r24,r25
python warehouse/chat/eval/ercot_speed_results.py --before runs/session143/before_sample.jsonl --after runs/session143/after_sample.jsonl runs/session143/after_rest.jsonl runs/session143/after_rest2.jsonl --summary
```

(The answers of tonight's runs are in the working copy `erw-143`, under `runs/session143/`, not in git.)

## The five most interesting numbers

1. **6.6 to 2.8** model calls for a number question: the old tool asked one identical query up to 8 times.
2. **15.1 to 6.4 seconds** to the words for the same 39 number questions; 5.5 seconds for the 29 that read once and
   write once.
3. **USD 2.16 to 1.42** for the same 78 questions: faster was also cheaper.
4. **2.9 seconds against 2.8:** the smaller model was not faster at planning, and made 2 of 7 answers twice.
5. **13.3 seconds** for one read of a year of hourly reserve prices: the slow tail is now the data, not the model.
