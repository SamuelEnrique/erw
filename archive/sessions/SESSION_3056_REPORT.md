# Session 3056: chain 166's third session (its 2262): the schema and the rules of the precise fields

Personal laptop, second window, 6 November 2026, about 12:45 to 14:15 UTC. Opus 5.5. Branch `wip/3056-policy` cut from `wip/3055-policy`.

## What it did

- `warehouse/policy/fields.py` (new): body, instrument, action_status, dates with their evidence, the next step with its date and evidence, the action's own figure with unit and evidence, docket ids in one form, and what each row's fields were read from. Written rules over the Register's record and the document's text; no model.
- `warehouse/connectors/policy_sources.py`: the listing asks the Register for `effective_on` and `comments_close_on`; the fields are derived where the printed text is read (and kept from the table for a row read before), for each release from its own words, and from the record and summary for any other row; the columns are added beside the table's own, every column the Digest and the page read unchanged; `widen_held` widens a table of any earlier shape, not only session 154's.
- `warehouse/policy/score.py`: one sentence added to the policy note on the sector (the audit's class 4).
- `tests/fixtures/policy/actions_3056.json` and `texts/` (30 stored actions with their texts and answers written from them), `tests/test_policy_fields.py` (14 tests).
- The audit file: counts corrected, the rows this session closes marked, a section "Session 3056"; `docs/methods/policy_monitor.md` section 14.

## What it found

- On the fixture: body, instrument, status, dates, next step and figure each 30 of 30.
- On the other 50 of the audit's sample (never used to write the rules): three faults, fixed. After them, on all 80: dates for 56 of the 62 rows that state one, none on another row; a figure for 12 of 16, none on another row; the instrument for 14 of 14; the body for 3 of 3.
- **Session 3055's audit had three errors, now corrected in the file:** class 1 is 62 not 59 (r39, r42, r66 missed); class 3 is 16 not 17 (r40 and r46's "17 gigawatts" is context; r30 was missed); and its remark that four FERC blanket-authorization notices state only a period was wrong, each states its date.
- Tests: `tests/test_policy_fields.py` 14 passed; the policy and periodicals test files (17 files) 423 passed, 12 skipped, before the last three changes; `test_policy_fields.py` and `test_session157.py` 45 passed, 1 skipped after them.

## Decisions made without you

- **No model in the fields.** Every field the chain lists for "the schema and the prompt" can be read by a written rule from the record and the text, with the sentence kept; a rule cannot invent. The prompt part is the scorer's one sentence on the sector.
- **New columns beside, never instead:** `action_status` beside `status`, `body` beside `agency`, `instrument` beside `action_type`, `figure_*` beside the empty `mw` and `price` (left as they are: their meaning in the events shape is the deal's, and a figure in kV or Dth/d is not a MW).
- **The fixture is actions, not stories** (a row of this table is a document); the texts are US government publications, kept to 20,000 characters (r66 whole), with each em dash of a source written as a colon and each en dash as a hyphen (the repository's rule).
- **Figures from the opening paragraph only**, so the context figures of a text (the coal orders' "17 gigawatts") are never taken for the action's; four real figures are missed for it.
- **The rows held are not rewritten here** (no warehouse data on this machine): the data machine's next run of the connector derives every row whose printed text is in its store.

## For Samuel's ruling

- Whether the 507 rows scored "policy" should be scored again under the new note (my estimate, not measured: 13 calls of 40 actions on the news scorer's Haiku model, under USD 0.50; the desktop's run, never this machine's).

## Cost

- Model: none (USD 0.00).
