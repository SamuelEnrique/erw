# Session 9815: `docs/security.md` brought up to date (chain 610, part B step 6)

Energy Research Warehouse (ERW). 20 November 2026, 20:18 to 20:19 UTC. The desktop's third window.

## What was done

- [`docs/security.md`](https://github.com/SamuelEnrique/erw/blob/main/docs/security.md), new section "The review of 20 November 2026": what was reviewed (the ground), the rule for a finding of high severity, four rows (one held back until its fix lands, T1 fixed and requested, T2 open for want of the key, T3 noted), what was read and found sound, the history (nothing to rotate), the dependencies, and what stands open and why. Nothing above the new section changed.

## Counts by severity

- High: 1, fixed on a branch, landing requested, held back until it lands.
- Medium: 0.
- Low: 3: T1 fixed and requested; T2 open (needs the key: the chat's evaluation set); T3 noted.

## Needs the key

- T2: the chat's earlier turns signed by the server. The change to what the chat sends needs the evaluation set run against the model. Cost not estimated here; the set's last full run is the guide (`docs/reviews/ask-eval-2026-11-13.md`).

## For Samuel's ruling

- T1: 30 tries an hour from one address, or session 177's rule back.
- The linter's packages: `npm audit fix --package-lock-only` now closes all seven findings with a minor version (developer-only); apply it, or leave L9 as it is.
