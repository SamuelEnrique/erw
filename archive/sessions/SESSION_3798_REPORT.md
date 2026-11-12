# Session 3798 report: a siting gap a public source can close: the grids' own reserve margins (CAISO)

Energy Research Warehouse (ERW). Chain 215, data machine (lab-desktop), 12 November 2026 16:51 to 17:03 UTC. Opus 5.5. Model spend USD 0. Requests: 4 of 25 (www.nerc.com's robots file; www.caiso.com's robots file and its 2026 summer assessment).

## Read these first

- **The siting gaps' row "Headroom, reserve margins by zone" gains the CAISO.**
  - `iso_reserve_margin_reports` (new, public): grid operators' reserve margins as their own assessments print them, from a registry of documents read by a session (`warehouse/sources/reserve_margins/`), as chain 211's tariff and rules registries are.
  - The CAISO's **2026 Summer Loads and Resources Assessment** (May 2026), for summer 2026:
    - an achieved planning reserve margin of **30.8 percent** in the tightest hour (page 15);
    - a requirement of **25 percent** for a 0.1 LOLE (page 15);
    - a surplus of **2,547 MW** above that target (page 3);
    - the CEC's 1-in-2 peak of **46,844 MW** in September, hour ending 18 (page 3);
    - a load-weighted RA PRM of **17.5 percent** (page 15).
  - Each figure carries its page and printed words.
- **NERC's Long-Term Reliability Assessment** (every area's margin) is closed to this reader: www.nerc.com's robots file disallows `ClaudeBot`, `anthropic-ai` and `Claude-Web` by name.
- **Written under the data lock,** before the data machine's own run took it at 17:00: 5 rows, validated, in coverage, archived (`20261112T165534Z-local`).
- **Registered:**
  - the license record (CAISO's verdict "may be public" agrees with the flag: **public**); `licenses.py` tables, check, write and status; the site's verdict and citation;
  - the release list (**held from v1** until the owner adds it, as chains 157's and 211's late tables are);
  - the live catalogue's hold until it is on Redivis;
  - the package's table record; the catalogue (`package/llms.txt`).
- **The Redivis draft upload waits** for the data lock (the data machine's run). Session 3805 does it.
- **Tests:** 3798 (new: the registry is clean, the CAISO's five figures, a bad file refused, an internal file not written). Then 275, 378, 410, 505, 237, 203, 238, 53, 67, 469, 1008, 1001, 1009, 3298 and 207: 175 tests, OK.

## Commits

`9beb3d521` (registry, connector, method, sector rule, test), `0097242cb` (table metadata and license record), `e4404237a` (release list, catalogue hold, package record), `d5dfaef24` (site verdict and citation).

## Decisions made without you

- **A registry, not a PDF parser:** the figures are typed from the document with page and words. A parser would need a PDF library the machine does not have, and the registry is the ERW's form for documents a session reads.
- **Held from v1** although public, as the late tables of chains 157 and 211 are: v1's list is yours to extend.
- **The CAISO's and ERCOT's margins are not compared:** each is its operator's own measure (the CAISO's in its tightest net-peak hour after batteries; ERCOT's at its peak load hour at ELCCs). Said so in the method note.

## For Samuel's ruling

- **Add `iso_reserve_margin_reports` to v1's package list.** Recommendation: yes, it is public and small. Default: held, on the drafts once uploaded.
