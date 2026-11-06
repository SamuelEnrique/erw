# The policy monitor's fresh audit (session 3139, chain 178)

The rules of chains 166 and 169 (`warehouse/policy/fields.py`, the place rule of `warehouse/connectors/policy_sources.py`) were written against the 80 actions of `docs/reviews/policy-audit-2026-11-06.md` and measured on them. This audit measures them on 80 others: every fifth row of rows 401 to 800 of the newest actions of the live set (5 June to 14 August 2026), read against their own documents, fetched on 6 November 2026 into the session's scratch folder (the Register's record and printed text, or the release's page; 80 of 80 answered). No rule was written from these 80 before this count. Their event ids, with the classes each shows, are in `policy-audit-2026-11-06-fresh-sample.csv`.

Sample: FERC 40, NRC 18, EPA 9, Interior 4, DOE 3, BLM 2, CPUC 2, PUCT 2.

## The count

| # | Class | Right | Faults | The faults |
|---|---|---:|---:|---|
| 5 | The instrument | 71 of 80 | 9 | r7 an EPA permit proposed, read as an application; r11 "Notice of Hearing" read as an application; r41 a feature story read as an award; r55 a revised review schedule read as a notice; r59 an EPA order on a petition read as an application; r69 a technical conference and r75 an open house read as a notice and an announcement; r76 a scoping period read as a meeting; r77 "Meetings" (plural) read as a notice |
| 1 | A stated date | 47 of 60 rows that state a step (counted again in session 3141: 51 of 59 at first) | 13 | r8 "answers ... are due by"; r51 and r55 a schedule written "Issuance of EA--August 21, 2026" (the printed text's own two hyphens); r59 a court petition's deadline; r65 "on or before 5:00 Eastern Time" (no "p.m.") for the applicant's amendments; r73 "commenting on the PAD ... must do so on or before"; r77 a meeting "held ... on"; r80 a deadline extended "from March 31, 2026, to October 30, 2026"; and, found in session 3141, r14, r27, r39 and r52, a court petition's deadline ("petitions for judicial review ... must be filed in the D.C. Circuit by"), and r63 an EA's date in a schedule |
| 3 | A stated figure | 10 of 12 | 2 | r26 and r72: the capacity stands past the first 1,800 characters read from a notice without a summary (at 3,863 and 2,188) |
| 9 | Out of scope, marked | 79 of 80 | 1 | r28, a National Park Service inventory of Native American remains held by a DOE office, not marked |
| 6 | The place | no fault found | 0 | (19 rows name no place; their state names are Washington, DC addresses or a nationwide rule's examples) |
| 8 | The body | 80 of 80 | 0 | (BSEE, NPS, OSMRE and the Texas Governor read right) |
| 2 | A status | 80 of 80 held | (with class 5's nine) | a status follows the instrument; the nine rows of class 5 carry a status of the wrong instrument |

Also seen, not counted as a class: r60, a correction that replaces an effective date ("June 4, 2026" to read "This RG is effective on August 18, 2026"), keeps the replaced date beside the new one; three release pages (r2, r66, r70) are PDFs, which the connector never reads (a release is read from its feed's title and summary).

**What it says of the rules**: on actions never used to write them, the dates hold for 86% of the rows that state a step (98% on the first sample), the instrument for 89%, the figure for 83%; the places and bodies found no fault. The first sample's numbers were rules written to fit; these are the honest ones.

## The rows closed by later sessions

(Sessions 3140 to 3144 write their counts here.)

- **Session 3140, class 5 (the instrument)**: 80 of 80 right on this sample (71 before), and no instrument of the first sample changed (14 of 14 there). The rules: an agency's order on a petition; a scoping period before its sessions; a hearing's notice, a technical conference, an open house and meetings (plural); an environmental review's schedule; a general permit proposed or issued as an approval ("Proposed ..." proposed); an award only with its words in the title or beside a sum of money. The NRC's "order imposing procedures" stays an application's notice. Tested with the nine rows' own titles and action lines.
- **Session 3141, class 1 (the dates)**: 60 of 60 rows right (47 before). The rules: "answers" and "commenting" as comment words; a schedule's "--"; an hour without minutes or "p.m." and a city's time; a meeting someone "will hold"; two kinds, `filing_due` ("must be filed ... on or before", a deadline extended "to" a date) and `review_petition_due` (a court petition's deadline); a date being replaced ("to read") left out. My first pass of this audit flagged only dates near words such as "due" and "deadline", so it missed five rows whose deadline reads "must be filed ... by" (r14, r27, r39, r52) or sits in a schedule (r63); the class is 13 faults of 60, not 8 of 59. On the first sample the rules add two true deadlines (its r7, "must be filed by October 31, 2029"; its r64, a court petition's) and change nothing else; on the archive's copy of the table they add 11 steps (6 filing deadlines, each an extended deadline, read one by one), and `check_policy.py` gives 299 of 299.
- **Session 3142, classes 3 and 9**: figures 12 of 12 (10 before): a notice without a summary is read for 4,000 characters, not 1,800 (r72's "1,900 million cubic feet per day", r26's "one 10,000 dekatherms per day (Dth/d) liquefaction system", the first of its two systems), and a figure after a stated total's words comes before the units listed ahead of it; no figure of the first sample changed. Out of scope 80 of 80 (79 before): an inventory under the Native American Graves Protection and Repatriation Act (r28) is on the written list; one record of the archive's copy is marked by it. Every class of the fresh audit now holds on its 80.
