# Session 2256 (chain 159, deals and datacenters) report: the six stated deals with no row

6 November 2026, from about 12:42 to 13:05 UTC, portable-laptop (code role), unattended. Worktree `erw-2254` on `wip/2256-deals`, cut from `wip/2255-deals`. Model spend **USD 0.0240** (one call, the switch on, on seven stories: 1,205 tokens in, 1,119 out, 4,148 cache write; measured, in `tests/fixtures/deals/recorded_2256.json`). No ledger row (a code machine; `ERW_LEDGER=0`). Nothing deployed; no warehouse data written.

- **Step 4 of the file**: the deals the stricter prompt drops. No ruling yet, so the rule is kept and a fixture holds the six.
- **The cause, read from the recordings**: all six clusters were sent, and the model returned `"deals": []` for each. Not the story selection, and not the code's party check (`fields.named_party` keeps a deal with one named party). Four reasons, not one (`docs/reviews/deals-audit-2026-11-06.md`, "Session 2256"):
  - D022, a plan ("plans $1.8 billion investment"): the prompt names this headline as not a deal; the two reads of the sample disagree on it (2231: not a deal; 2249: missed).
  - D031 (Sellafield's partners unnamed) and D092 (Crescent's buyer unnamed): one party named. **These two are what chain 156's ruling 2 is about.**
  - D084, Shell's sale of Jiffy Lube to Monomoy Capital: two parties named; an asset that is not an energy asset.
  - D061, a commentary headline that names a deal; D071, a valuation of an AI cloud.
- **The switch**: `ERW_DEALS_ONE_PARTY=on` (`warehouse/deals/extract.py`) adds one sentence to the prompt; off, the default, leaves the prompt identical to the committed one (checked by comparing the two strings, and by the test).
- **The fixture**: `tests/fixtures/deals/stories_2256.json` (the six clusters, seven stories, from the 2249 set). Off: the 2249 answers replayed, 0 rows. On: `recorded_2256.json`, 3 rows (D031 Sellafield the buyer; D084 Shell to Monomoy, USD 1.3 billion; D092 Crescent the seller, no buyer). D022, D061 and D071 get none either way.
- **Tests**: `tests/test_session2256_deals.py`, 5 passed; the chain's deals tests and test 531: 132 passed.
- **The method note** (`docs/methods/energy_deals.md`, "A deal with one party named") says what the switch does and its default.

## Decisions made without you

1. **The rule kept and a switch added**, as the file's step says when no ruling has come: the owner's answer is the switch's default, one line.
2. **The switch is an environment variable read when the module loads**, so the fixture can record both settings and the daily run needs no change for the default.
3. **The ruling's question restated**: it concerns two of the six, not six; D084 raises a separate question of scope.

## For Samuel's ruling

1. (Chain 156's ruling 2, narrowed) A sale or award with one party named and the other not (Crescent's D-J assets, Sellafield's partners): keep it (`ERW_DEALS_ONE_PARTY=on`), or leave it out (the default now).
2. A sale by an energy company of an asset that is not an energy asset (Shell's Jiffy Lube, USD 1.3 billion): a deal for the tracker, or not. With the switch on, the model returns it; off, it does not.
