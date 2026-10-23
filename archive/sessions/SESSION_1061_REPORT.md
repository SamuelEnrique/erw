# Session 1061 report: the Digest's revised WTI, proposed

23 October 2026, about 07:45 UTC (written while chain 071's landing held the build lock), on samueloldlaptop, unattended, on `wip/1042-allgrids`. Chain `queue/done/072-day-23-october-code-allgrids-packages-2.md`, session 1061. Model spend USD 0. No request (the archive's bucket was not read); no build.

## Read these first

- **`docs/reviews/digest-revisions-proposal.md`** (new): why check-values fails the 21 October Digest's WTI for 14 October (101.91 printed; EIA revised the close, the table now reads 96.34), and two ways a check could know a source's revision: **A**, a figure record a Digest issue (`docs/digest/figures/<date>.json`, written by `warehouse/news/brief.py`: each figure's value as printed, its table row's key and `retrieved_at`), read by `check-values.mjs` and `scripts/check_digest.py` (recommended); **B**, the check restoring the table from the archive's bucket as of the issue's time (needs the service key; not for GitHub's code-branch run). Nothing is wired and no past issue is rewritten.
- The failure stays until 23 November (the 33 days check-values keeps a Digest among its pages).

## The landing

Lands with the next landing of this chain.

## Decisions made without you

1. **A is recommended over B**: a record written when the issue is written needs no key and no download at each gate. Reversible: the proposal is a document.

## For Samuel's ruling

- Whether to adopt A, B or neither (the failure read by hand until 23 November).
- Whether a revised figure on a past issue gets a visible line, or stays as printed.
