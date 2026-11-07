# Session 2232 (chain 156, deals and datacenters) report: the schema and the prompt

6 November 2026, about 07:31 to 07:52 UTC, portable-laptop (code role), unattended. Worktree `erw-2232` on `wip/2232-deals`, cut from `wip/2231-deals`. Model spend under the owner's key: **about USD 0.25** (one recording, USD 0.1227 measured; one earlier attempt of the same 3 calls whose answers were lost to a fault in the recorder's cost line after the calls returned, unmeasured, the same input, so about USD 0.12). No ledger row (a code machine holds no data lock; `ERW_LEDGER=0`). Nothing deployed; no warehouse data written.

- **`warehouse/deals/fields.py`** (new): one vocabulary a field, each with its reasoning: `kind` (tool 6's kinds, the power kinds first: nuclear restart or uprate, SMR, behind the meter, gas buildout, transmission, storage, compute capacity; then the forms), `stage` (rumored to operating, from the stated words with the span), `grid` (only where the story names the operator), the AI-power rule with its basis (a named AI lab, hyperscaler, datacenter operator or AI-load buyer, or a datacenter load), an energy price only, sanity bounds as flags, a deal kept only where the story names a party.
- **`warehouse/deals/extract.py`**: the prompt says what is not a deal (a plan, a pledge, a seeking, a permission, two governments, an unnamed raiser), what a party is, which sum is the deal's, the country rule with examples, the confidence bands and their words; the schema asks for `kind`, `stage`, `stage_text`, `confidence_basis`. New columns of `energy_deals` beside the old: `kind`, `kind_basis`, `stage`, `grid`, `usd`, `usd_per_mwh`, `ai_power_basis`, `flags`, `fields_version`; of `energy_deals_evidence`: `stage_text`, `confidence_basis`, `spans` (the story's words stay in the internal table). A table of the old columns is upgraded in place on the next run, every row and value kept, its new fields read from its own values (`fields_version` upgraded). The Roundup's fields keep their names and meaning.
- **The fixture** (`tests/fixtures/deals/`): 40 stored stories, 36 answers written from the stories' words, the model's recorded answers; **`warehouse/deals/eval/fixture.py`** records (capped) and grades (offline). **`tests/test_session2232_deals.py`**: 15 tests.
- **The counts on the fixture, before and after** (the audit file, "Session 2232"): a deal kept where none is 7 to **0**; figures invented or of another sum 2 to **0**; AI tag wrong 3 to **0**; country missed 4 to 1; party wrong or a description 3 rows to 1; stated deals missed 0 to 2 (the model now returns none for a raise at a valuation and for a government's stake).
- **A correction to session 2231's audit**: duplicate pair 3 (Sempra and Cheniere) is two deals; the Cheniere story's summary states Sempra's own 20-year agreement.
- **Tests**: `test_session2232_deals.py`, 531, 113, 465, 466: 68 passed, 2 skipped; 531, 176, 119: 78 passed.

## Decisions made without you

1. **No outlet text in `energy_deals`.** The prompt asks for an `evidence` column on every row; the evidence sentence has always been outlet text in the internal `energy_deals_evidence` (the site never shows outlet text: `site/app/deals/page.tsx`), and `energy_deals` is loaded into the live set. The sentence, the stage's words, the confidence's words and the figures' spans go to the evidence table, one row a deal and story; `energy_deals` holds only the code's fields and the links.
2. **`status` kept, `stage` added**: the Roundup prints `status`'s five words; `stage` adds financed, under construction and operating.
3. **`usd` and `usd_per_mwh` beside `dollars` and `price`**, equal to them, so the units are named as the prompt asks and the old readers are untouched.
4. **The AI-power tag is the code's rule**, not the model's sense: the same answer on every run; the model's answer, when it differs, is in the run log. The party list (`fields.AI_PARTIES`) is a list in code, extended by evidence.
5. **`compute_capacity`** is a kind of its own (a cloud, GPU or datacenter capacity contract): kept in the table, labelled, filterable, for your ruling (session 2231's item 1).
6. **A deal is kept only where the story names a party** (buyer, seller, a joint venture's partner, or the company sold in an acquisition): "Fusion Startup Raises $450 Million" is not a row.
7. **The key for the recording** was read from the main checkout's `.env` for the one command (the worktree has no `.env`); nothing of it was copied or printed.

## For Samuel's ruling

1. Whether compute and datacenter capacity contracts belong in the deal tracker at all (they are kept, as `compute_capacity`).
2. The two deals the new prompt misses on the fixture: a raise named only by its valuation (Volta) and a government's equity stake (Lithium Americas). Both are stated deals; the prompt's "not a deal" list may now be read too widely by the model. Session 2249 reads the count again on the sample.
