# Session 2275 (chain 174, deals and datacenters) report: a party wrong

6 November 2026, about 13:42 to 13:49 UTC, portable-laptop (code role), unattended. Worktree `erw-2254` on `wip/2275-deals`, cut from `wip/2274-deals`. Model spend **USD 0** (code; the answers replayed). Nothing deployed; no warehouse data written.

- **The class**: a party wrong, 1 of 106 on the second read (D001: Google, the credit backstop, as seller).
- **The fix**: `fields.credit_parties`, used by `extract.py` where no buyer is named: the seller the evidence names as providing credit becomes the buyer, the company named after "for" the seller, out of `other_parties`. Logged.
- **Before and after**: **1 to 0**; every replayed row's parties diffed on the three deal fixtures: only D001 changed. A first run listed TeraWulf twice in `parties` (it was also an other party); fixed before the commit.
- **Tests**: `tests/test_session2275_deals.py`, 3 passed (one form of mine, "provides $3.5 billion financing", failed at first: a sum between the verb and the word; the rule now lets three tokens of any kind stand there); the deals and datacenter tests, 271 passed, 1 skipped.
- **Docs**: `docs/methods/energy_deals.md` ("The provider of credit"); the audit file's section, with what is left of the audit.

## Decisions made without you

1. **Only where no buyer is named**: a deal with a buyer keeps its parties as the model gave them.

## For Samuel's ruling

- None new.
