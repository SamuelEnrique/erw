# Session 9801: the rulings read a second time (20 November 2026)

Energy Research Warehouse (ERW). Machine: SamuelPersonal (Samuel's own laptop). At the owner's instruction of 20 November, about 12:05 PST: a second reader of the 54 recommended switches and 48 recommended keeps of `docs/reviews/rulings-one-sitting-2026-11-19.md`, trusting nothing, until the laptop closes at about 13:00 PST. Session 9801 was checked free on origin/main and every branch with 9800 to 9809. Model spend USD 0: no model API called. No build, no browser, no test suite.

## What was done

- **The file:** https://github.com/SamuelEnrique/erw/blob/main/docs/reviews/rulings-second-read-2026-11-20.md, one row an entry with its verdict, its reason and the addresses checked; at the top the counts and the entries not to rule by group.
- **How:** with about 50 minutes left when the instruction came, the 102 entries were split among six readers working at once (Claude Code's own agents, inside the session's allowance; no API key), three for the switches and three for the keeps, each in the ranked list's order (the largest change first inside each section). Each was given the entries and the method (a publisher's robots file and terms before its page; a ruling of Samuel's read in `docs/state/`; the tool's method note) and none of the first session's conclusions beyond the entry's own words. Each wrote its rows to a scratch file as it went; `runs/c9801_assemble.py` built the review file from them and `runs/c9801_push.sh` pushed it about every ten minutes.
- **The weekend pack:** one line added to part 2 pointing at the file; nothing else there changed.

## What came out

- **All 102 entries read:** holds 42, holds weakly 53, does not hold 1, could not check 6.
- **Not to rule by group (7):** 11 (a keep that says Samuel ruled; the note shows the question still waiting, default 0); 4, 114, 123, 126 (the figure rests on Berkeley Lab's or FERC's page, which answered 403, or a report not found); 45 (the Virginia statute's host disallows every automated reader in its robots file, so the first session's read of it should not have been made); 111 (NOAA's record not fetched in time).
- **Holds weakly (53):** mostly a ruling made for another table, a default a session wrote into a method note, or the general page standard, used as if it decided the question. Listed apart, with the reason in each row.
- **Corrections the readers found inside entries that hold:** 65 (EIA now gives about 1,037 Btu a cubic foot for 2025; the ruling should name the year); 107 (the market monitor prints 1.83 hours, so "about 1.9" is wrong under either choice); 93 (the keep is right but its reason is wrong: EIA's and ICE's terms were read, and both need written permission); 32 (K.S.A. 79-213 (l) lists 26 kinds, not 25); 34 (Wisconsin's Tax 11.10(3)(f) exempts the direct-current wiring, so the materials are partly exempt).
- **The network dropped** from about 20:15 to 20:35 UTC; four readers stalled and were restarted. Some government hosts' terms pages were skipped for time (their robots files allowed the pages), and keeps 75 to 128 were checked against the repository only. The file says so at its top.

## Decisions made without you

- **Six readers in parallel, not one in order.** The instruction asked for the switches first and then the keeps; one reader could not have reached the keeps before 13:00 PST. The switches and the keeps were read at the same time, and the file lists the switches first.
- **"Largest change first" is the ranked list's own order** (its sections, then the largest percent inside each), which the entry numbers follow.

## For Samuel's ruling

- Each entry under "Do not rule these by group" in the file.

## Needs the key

- Nothing.
