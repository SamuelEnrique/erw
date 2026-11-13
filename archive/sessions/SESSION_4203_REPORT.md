# Session 4203 report: the tests (chain 239, window 4)

13 November 2026, about 10:46 to 10:50 UTC. Branch `wip/4200-forecast`. Model spend USD 0.

- **`site/scripts/test-forecast.test.mjs`**: 15 node tests, every formula against hand arithmetic: the deflator; the defaults; JEDI's own figure at JEDI's own spending, and scaling with spending only; operations per MW (DC for PV); the even spread; income tax (Texas, Illinois, Iowa's credit, Ohio's untaxed band, California's brackets walked by hand); Nebraska, South Dakota (and its 5 MW floor), Minnesota's tiers and exemptions, Iowa's schedule year by year, the reader's own rate; sales tax with an exemption and geothermal's absence; severance's volume and price; the present value. 15 of 15 pass.
- **`tests/test_session4203_forecast.py`**: runs them, and checks every parameter file names its source, every statute rule quotes its statute, the taxable shares are their arithmetic, the deflator stops at 2025, the note is internal, and no dash. 9 of 9 pass.
- **Fixture** `tests/fixtures/forecast/jedi_rows.json`: 768 rows of `nlr_jedi_multipliers` for eight states with NLR's notice (the table itself is not in git).
