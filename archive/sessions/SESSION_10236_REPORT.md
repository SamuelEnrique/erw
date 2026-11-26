# Session 10236 report: the home page, the tour and the Thesis Builder audited

Chain 710, part D, the old laptop, 26 November 2026. Worktree `C:\Users\lossa\Documents\erw-c710-a`, branch `wip/audit-home-doc`.

## What was done

- `docs/reviews/home-model-audit-2026-11-26.md` and its evidence folder: the ground, every home-page figure and every tour number restated from their own files and drawn with the site's own code, the Thesis Builder's computations without a model restated (the gate on 100 inputs, the five saved runs' funnels), what an upload holds and where it goes, the spending guard, 14 numbered findings.
- The numbers are right: 0 gaps on every figure restated.
- Branches: words `wip/audit-home-1` to `-5`, `-7` to `-14`; merged as `wip/audit-home-words` at `51eca33ab` (all but `-8`; 793 passed, 42 skipped, 1 failed, `test_session156`'s node test, failing on clean main too); tests only, for ruling, `-6`, `-15`, `-16`.
- No model called (`ERW_SPEND_CAP_USD=0`), no request to any service, no table written, no lock taken.

## Decisions made without you

- `wip/audit-home-8` (the tour's Digest stop) is words only but is kept out of the combined branch: session 9601 left that stop "for the owner's ruling". It is returned as ready, for your yes.
- The tour's line in `site/lib/pages.ts` no longer carries a count ("Twelve stops ... eight minutes" was stale twice); `tests/test_session292.py`'s assertion of it was changed with it. `tests/test_session135.py`'s assertion of the method note's old sentence was changed with finding 13's words.
- The home strip's `latest_prices` is not held on this machine: the drawing answered it with hourly rows of `iso_rtm_hub_prices`, and the strip is drawn, not restated.

## For Samuel's ruling (default "left as it is")

- Finding 1, `wip/audit-home-15`: the home page's Digest block reads the new form's "What moved" when "Top of the industry" is absent. Effect: 5 stories drawn instead of "no data".
- Finding 6, `wip/audit-home-6`: a held grid's figure on the strip drawn without its unit and interval time. Effect: 3 times and 3 units not drawn.
- Finding 13, `wip/audit-home-16`: a Thesis Builder sentence holding a number no cited source holds is not shown. Effect on the five saved runs: 49 texts replaced by "not confirmed".
- Finding 8, `wip/audit-home-8`: land the tour's Digest stop words (session 9601 left it for you).
- `/privacy` names no Thesis Builder store and does not say a niche may go to Anthropic's model (internal view only); not changed.

## Needs the key

- Nothing.
