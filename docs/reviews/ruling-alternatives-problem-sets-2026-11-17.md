# Ruling alternatives: /learn/problems (17 November 2026)

Session 7717 (samueloldlaptop, claimed in `docs/state/ruling_alternative_claims.md`). For each line of `docs/reviews/ruling-impact-problem-sets-2026-11-17.md` whose change is 1 percent or more, or that adds or removes a figure, the other choice would be built on its own branch from origin/main, with a test that pins the figure under it. No branch was built for this tool; no default on main changed.

- **Line 1 is not built: it needs data not held, and what can be computed moves the answer under 1 percent.** The other choice, question 4 of "Storage and taxes" at New Mexico's October 2026 rates, needs the Taxation and Revenue Department's table from September 2026 on, which the rules file (`site/data/severance_rules.json`) does not hold; extending it is a read of a publisher's page, for the data machine or a person, not a code change here. The one rate that table changes by the price of oil, the conservation tax, gives at 0.19 percent USD 7,236.51 against the answer key's 7,287.54 (-0.70 percent) and at 0.24 percent no change; the other two rates are not known. A branch would carry a guessed rate, which the warehouse never does.
- **No model call** was made (spend USD 0).

| # | Line | Branch | Figure, main's rule | Figure, the other choice | Files touched | Test | Browser row |
|---|---|---|---|---|---|---|---|
| 1 | Read New Mexico's table for September 2026 on and extend the rules file, so question 4 of "Storage and taxes" uses October's rates | none built (data not held) | USD 7,287.54 at the newest rates held (1 April to 31 August 2026: severance 3.75, emergency school 3.15, conservation 0.24 percent), 1,000 bbl at October's mean of USD 102.066364 | Not computed: October's rates are not held. At a conservation rate of 0.19 percent USD 7,236.51 (-0.70 percent); at 0.24 percent no change | none | none | 339 |
