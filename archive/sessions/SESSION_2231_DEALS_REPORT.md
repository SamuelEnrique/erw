# Session 2231 (chain 156, deals and datacenters) report: the audit of the stored records

6 November 2026, about 07:25 to 08:05 UTC, portable-laptop (code role), unattended. Worktree `erw-2231` on `wip/2231-deals`, cut from `wip/2230-deals` (origin/main merged). Model spend under the owner's key **USD 0** (no call: the prompt's "Pulls: none"). Nothing deployed; no warehouse data written.

- **The sample**: 106 deals (every fifth of the newest 600 by extraction time; the table holds 529) and 60 facilities spread over the 163 rows; each row read against its stories' stored title and summary by three readers of this Claude Code session on one rubric, six of their calls read again by the session and confirmed. Every row's grade and note, the scripts and the rubric: `docs/reviews/deals-audit-2026-11-06/`.
- **The fault classes**, numbered, counted, three quoted examples each: `docs/reviews/deals-audit-2026-11-06.md`, "The audit of the stored records". The largest:
  - deals: place missed 17 of 106; status missed 14; not a deal 12; kind wrong or no word for it 11 (gas buildout, pipeline, compute capacity); a party a description 7; AI-power tag wrong 6 (Amazon and AEP's 960 MW nuclear pact tagged false); a party wrong 4;
  - **no figure in the sample is invented or of the wrong value**: every figure fault is a figure missed (MW 3, USD 2, term 1) or a figure of another sum of the story (USD 2, a stake's 80% kept as a price);
  - facilities: MW with no IT or total basis 14 of 60; status missed 9; confidence too low 6; not a facility 5; state missed 5; three rows fold several facilities into one.
- **Duplicates over the whole tables**: three open deal pairs (the Roundup audit's Vistra loan and Amazon and Constellation pairs, still not in the register though the code's rule matches both; Sempra read in place of Cheniere); no facility repeat.
- **What the stored text allows**: 6 of 18,358 scored stories state a price per MWh; the median summary is 77 characters. The comparables will be thin whatever the extraction does; written in the audit as the first limit.
- **The empty W44 tables** explained: five failed days on the spending limit (only the digest's line kept the API's words), no daily run 31 October to 4 November, the scorer stopped with 1,092 left.
- **Rows A1 to A16** at the audit's end name the class each later session takes.

## Decisions made without you

1. **106 deals, not 120**: the prompt's rule (every fifth of the newest 600) gives 106 on a table of 529; the rule was kept rather than the count.
2. **Readers**: the 166 rows were read by three subagents of this session on one written rubric (in the folder's README), not by the owner's model key; the session confirmed six of their calls. Their judgement calls are listed in the audit (debt roles, fund closes, euros).
3. **The sample and the grades are committed** under `docs/reviews/deals-audit-2026-11-06/` (short quotes of headlines, as the Roundup audit quotes them), so the second read (session 2249) grades the same rows.

## For Samuel's ruling

1. Compute and datacenter capacity contracts ("OpenAI, Amazon Sign $38 Billion Cloud Deal", "Agrees to Rent CoreWeave AI Capacity") are stored as offtakes and leases: the readers counted them as not energy offtakes. Session 2232 gives them their own kind, `compute_capacity`, kept in the table and filterable, unless you say they belong out of an energy deal tracker.
2. Debt deals: the lender as buyer, or the borrower? The stored rows do both. Session 2234 makes the lender the buyer (the extractor's own rule for debt and project finance) unless you rule otherwise.
