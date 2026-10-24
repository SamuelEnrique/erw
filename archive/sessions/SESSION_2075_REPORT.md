# Session 2075 report: the licenses' fifteenth round (JODI and the Energy Institute read ahead)

23 October 2026, from 20:22 UTC, on lab-desktop (the data machine), the sixth session of `queue/done/067-day-25-october-data-neighbours-emitters-disasters-world-oil.md` (run while session 2074's notes were being written). Model spend USD 0. Pulls: 7 requests of 20 (the robots files of www.jodidata.org, www.energyinst.org and www.ief.org, each in a call of its own; JODI's home page and its oil data downloads page; the IEF's home page and its Terms and Conditions). Reads 230 to 236 (199 to 205 when written; renumbered after chains 057, 058 and 066's reads at the merges with main in sessions 2080 and 2083).

## Read these first

- **Sessions 2070 to 2073's publishers have verdicts:** the IESO (new in session 2070, read 225, may be public), the AESO (read 46), EPA (read 55) and NOAA NCEI (reads 9 and 182). This round read ahead the publishers of sessions 2076 and 2077.
- **JODI: needs written permission, taken from its host's terms** (a new verdict on read 236). www.jodidata.org states no terms of reuse: its home page links none and its downloads page shows only "Copyright JODI 2026" (reads 231, 232). The International Energy Forum, which runs it, says for ief.org: "You agree that you will not use any robot, spider, other automatic device, or manual process to monitor or copy any Website pages or any content included therein without IEF's prior written permission", and allows reproduction only for "personal, informational, non-commercial use". **So session 2076 pulls no JODI data,** and the question goes to Samuel.
- **The Energy Institute refused the ERW's reader at its robots file** (HTTP 403, read 233): www.energyinst.org joins the hosts not asked again without a ruling, and session 2077's Statistical Review cannot be taken.
- **The record's bound is raised:** `tests/test_session205.py` allowed 203 reads; the record held 205 then (`+ 20`, with its comment), 236 after the merges with main. Chain 057 landed with its reads renumbered 192 to 195 (after chain 059's 191), so this chain's were renumbered 196 to 209 at session 2080's merge, 216 to 229 after chain 058's 196 to 215 at session 2083's first, and 223 to 236 after chain 066's 216 to 222 at its last; chain 058's, unlanded, are renumbered at whichever of the two lands later.

## Errors

- None.

## Decisions made without you

- **The IEF's terms taken for JODI** (reversible by a ruling): the conservative reading while JODI's own site states none.

## For Samuel's ruling

- **JODI's oil database:** ask the IEF (or JODI) for permission to read its downloadable files automatically and republish country figures with attribution, or rule that jodidata.org's silence allows it.
- **The Energy Institute's Statistical Review:** its site refuses the ERW's reader; whether to ask the Energy Institute for access.

## Files

- New: this report.
- Changed: `warehouse/metadata/license_reads.csv` (230 to 236), `license_verdicts.csv` (JODI), `docs/licenses.md`, `tests/test_session205.py` (the bound).
- On the data machine only: `runs/c067/s2075/`, `runs/license_reads/s2075/`.
