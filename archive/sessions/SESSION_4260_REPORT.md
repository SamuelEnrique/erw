# Session 4260 report: North Carolina, Michigan and Vermont held (chain 240, window 4)

13 November 2026, about 14:41 to 15:32 UTC. Branch `wip/4250-forecast`. Model spend USD 0. Requests 87 to 99 of `runs/w4/probe.csv` (ceiling 120), robots files first.

- **North Carolina** (ncleg.gov; robots asks a 2-second crawl delay, honoured): G.S. 105-275(45) excludes 80 percent of the appraised value of a solar energy electric system ("all equipment used directly and exclusively for the conversion of solar energy to electricity"), with no end date. Held as Florida's rule kind with no end year, PV only, on the reader's own rate.
- **Michigan** (legislature.mi.gov, which has no robots file: 404; requests 91 to 94, a few seconds apart): the Solar Energy Facilities Taxation Act (2023 PA 108). A city, village or township may establish a district and approve a certificate for a facility of at least 2 MW AC; the facility (not its land) is exempt from property tax for 20 years and pays USD 7,000 per MW AC a year, or USD 2,000 on state land, in an opportunity zone, on a brownfield or attached to an improvement. Held as Oregon's local option: off by default, default USD 7,000, a typed rate held to 2,000 to 7,000.
- **Vermont** (legislature.vermont.gov; 30-second crawl delay honoured, each request after a 31-second sleep; two section addresses were wrong and the title and chapter listings found 32 V.S.A. 8701 in chapter 215): USD 4 per kW a year on solar plants of 50 kW or more, paid to the Education Fund. Held as a capacity tax that adds to the reader's own property tax rate, as Wyoming's excise does.
- **Code**: the Python file now counts a capacity tax that adds to the property tax (it did so only for a production tax); the do-file adds the reader's rate once after the rules, and writes an exclusion with no end year without `undefined`. The model's note for an option that is off says "the local option is off" (Michigan's districts are no county's).
- **Tests**: node 33 of 33 (three new tests, two new replication pairs: North Carolina and Vermont, Michigan with the option on); the fixture adds the three states' JEDI rows (288). Python forecast and pack tests 42 passed.
- **Built and read** under the build lock (waited 14:50 to 15:22 for window 2's `w2-s4007`; built 15:23): check-values 785 of 785 on the five addresses, and 152 of 152 on a sixth, `/impact?tech=utility_pv&state=mi&iaval=1&bstate=vt&bown=1.4&bownyears=25` (Michigan USD 1,050,000 a year; Vermont USD 600,000 plus 1.4 percent of the falling cost). Read at 1280 and 390 px: no sideways scroll, no console error; North Carolina at 0.7 percent gives USD 329,387 the first year.
- **After merging `origin/main`**: the 179 related test files 2,218 passed, 56 skipped, 0 failed.
- **Landing row 4** moved to `000cce004` on main (`66a2d5331`).

## Decisions made without you

- Michigan's two statutory rates are offered as a range from 2,000 to 7,000, as Oregon's is, with the tip saying only the two ends are statutory. A rate between them is held, not refused.
- Michigan's 20 years are counted from the first operating year; the statute counts them from the certificate's date, usually before construction, so the tool may give one or two years too many.
- Vermont's "plant capacity" (defined in 30 V.S.A. 8002, not read) is taken as the reader's MW AC.

## For Samuel's ruling

- Whether a Vermont solar plant also pays the education property tax on its fixtures (32 V.S.A. chapters 121 to 135, not read). Default: not held, so the reader's own rate stands for every property tax beyond the capacity tax.
