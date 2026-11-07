# Session 3401 report: the classification behind the Attention and Friction indices (chain 202)

6 November 2026, 19:27 to about 19:52 UTC, on lab-desktop, fourth window, chain 202, unattended, Fable 5.1. Model spend USD 0.75 (32 calls, all in `api_cost_ledger` under session 3401; USD 0.30 of it the two trial runs that failed on a bug of mine before the answer was read, see below). Pulls: none; the model calls were the only requests.

## Read these first

- **The classifier** is `warehouse/derived/attention_classify.py`: for each story (title and summary; the corpus holds no body) a fixed model answers its sector (the indices' seven, `other_energy` or `not_energy`), whether it is about the US, the one state, the county, city or metro named, whether it reports opposition, the kind of opposition (moratorium, lawsuit, protest, permit denied, rate case, political opposition, other) and its tone. The answer is a JSON schema the API enforces; every value is then normalised by code (`norm_row`: an unknown enum or state code is emptied, never guessed, and the row says what was fixed). The indices are not computed here: the next session's `attention_index.py` counts the classified rows.
- **The hand-labeled set** is `tests/fixtures/attention/labeled_200.csv`: 200 stories drawn by `draw_sample` (seed 3400), 100 from stories whose text holds an opposition word and 100 from the rest, each labeled by this session from its title and summary. It holds 18 opposition stories (lawsuit 5, political opposition 4, other 3, protest 3, moratorium 2, permit denied 1), 99 energy stories (datacenters 24, other energy 23, oil and LNG 21, transmission 8, nuclear 7, storage 6, gas 5, solar and wind 5), 101 not about energy; 84 about the US, 17 with a state, 6 with a named place.
- **The two models' answers** are stored beside it (`model_200_sonnet.csv`, `model_200_haiku.csv`) and `tests/test_session3401_attention.py` (14 tests, passing) reads them offline: no test calls a model.

## Accuracy against the hand labels (200 stories)

| Field | Sonnet 5.5 | Haiku 4.5 |
|---|---|---|
| opposition (yes or no) | 0.985 | 0.975 |
| friction F1 (precision, recall) on the 18 opposition stories | 0.914 (0.941, 0.889) | 0.857 (0.882, 0.833) |
| kind of opposition | 0.985 | 0.950 |
| sector, all nine classes | 0.920 | 0.915 |
| sector, among stories labeled in an index sector | 0.987 | 0.934 |
| about the US | 0.930 | 0.795 |
| state | 0.985 | 0.985 |
| place (first word) | 0.980 | 0.975 |
| tone | 0.870 | 0.725 |

- Sonnet's two opposition misses are the EU combustion-engine ban stories labeled `other_opposition` (industry pressure undoing a policy), a debatable label; its one false positive is a Senate permitting deal story. Haiku misses two of five lawsuits and calls two fifths of the US stories not US (recall 0.619 on `us`), which would misplace the national counts.
- Tone is the weakest field on both; it is reported on the page as a mean and said to be the least reliable field in the method note.

## Cost per thousand stories (the compact schema, prompt version 2)

| Model | USD a call of 40 | USD per 1,000 stories | Stories for USD 3 |
|---|---|---|---|
| Sonnet 5.5 | 0.028 | 0.71 | about 4,200 |
| Haiku 4.5 | 0.012 | 0.29 | about 10,300 |

- The first schema (long keys, the 22-character id in every answer) cost USD 0.89 per thousand on Sonnet; the answer's keys were shortened and the story is named by its number in the batch (`KEYS` maps them back), which cut the output tokens by a quarter at the same accuracy. Output tokens are still about two thirds of a call's cost.
- Haiku's system prompt is under the model's caching minimum, so its calls read no cache; Sonnet's read the cached prompt from the second call.

## The cap for this chain's run

- **Model: Sonnet 5.5** (`ATTENTION_MODEL`), for the friction precision and the US field. **Cap: USD 3 a session,** sessions 3402 and 3403: about 8,400 stories of the corpus's 26,438, the newest first.
- **Stories the news scorer gave significance 0 are not sent** (4,929 of the 26,438; the rubric's "not energy relevant"): they stay in each week's denominator as unclassified, and the method note says so. The eligible corpus is about 21,500 stories, so the two sessions reach roughly the newest 40 percent, which is about the dense weeks since 21 September 2026. The weeks before are left for file 203's sessions 5 and 6, named in the run reports.

## Decisions made without you

- **Sonnet 5.5 over Haiku 4.5** at two and a half times the cost per story, for friction precision 0.94 against 0.88 and the US field 0.93 against 0.80. The alternative, Haiku over nearly the whole corpus for the same money, is listed for the owner below.
- **The labels are the session's own reading** of 200 titles and summaries; where a story's opposition is arguable (industry pressure undoing a policy) it was labeled `other_opposition`.
- **Significance-0 stories left unclassified** to stretch the cap, counted in the denominators.
- **Prompt version 2** (short keys, batch index) is the one the run uses; version 1's trial is recorded only in this report and the ledger.
- **The classifier writes outside the warehouse** (`warehouse/raw/attention/classified_<run>.jsonl`, appended call by call) and the table writer reads those files under the data lock, so a long run never holds the lock and a stopped run keeps what it classified.

## For Samuel's ruling

- **Coverage against precision:** for the same USD 6, Haiku would classify nearly the whole corpus (about 20,000 stories) at friction F1 0.86 and a US field of 0.80; Sonnet classifies about 8,400 at F1 0.91 and 0.93. This chain takes Sonnet; a word from you can switch the next chain's second pass.
- **The two trial runs that failed** before reading the answer cost USD 0.30 (a bug in my batch loop, fixed in the same session). It is in the ledger under session 3401.

## Next

Session 3402: `attention_index.py` (the three tables from the classified rows), the first run under the cap, the locked write.
