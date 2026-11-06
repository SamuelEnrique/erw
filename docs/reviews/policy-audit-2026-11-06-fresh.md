# The policy monitor's fresh audit (session 3139, chain 178)

The rules of chains 166 and 169 (`warehouse/policy/fields.py`, the place rule of `warehouse/connectors/policy_sources.py`) were written against the 80 actions of `docs/reviews/policy-audit-2026-11-06.md` and measured on them. This audit measures them on 80 others: every fifth row of rows 401 to 800 of the newest actions of the live set (5 June to 14 August 2026), read against their own documents, fetched on 6 November 2026 into the session's scratch folder (the Register's record and printed text, or the release's page; 80 of 80 answered). No rule was written from these 80 before this count. Their event ids, with the classes each shows, are in `policy-audit-2026-11-06-fresh-sample.csv`.

Sample: FERC 40, NRC 18, EPA 9, Interior 4, DOE 3, BLM 2, CPUC 2, PUCT 2.

## The count

| # | Class | Right | Faults | The faults |
|---|---|---:|---:|---|
| 5 | The instrument | 71 of 80 | 9 | r7 an EPA permit proposed, read as an application; r11 "Notice of Hearing" read as an application; r41 a feature story read as an award; r55 a revised review schedule read as a notice; r59 an EPA order on a petition read as an application; r69 a technical conference and r75 an open house read as a notice and an announcement; r76 a scoping period read as a meeting; r77 "Meetings" (plural) read as a notice |
| 1 | A stated date | 51 of 59 rows that state a step | 8 | r8 "answers ... are due by"; r51 and r55 a schedule written "Issuance of EA--August 21, 2026" (the printed text's own two hyphens); r59 a court petition's deadline; r65 "on or before 5:00 Eastern Time" (no "p.m.") for the applicant's amendments; r73 "commenting on the PAD ... must do so on or before"; r77 a meeting "held ... on"; r80 a deadline extended "from March 31, 2026, to October 30, 2026" |
| 3 | A stated figure | 10 of 12 | 2 | r26 and r72: the capacity stands past the first 1,800 characters read from a notice without a summary (at 3,863 and 2,188) |
| 9 | Out of scope, marked | 79 of 80 | 1 | r28, a National Park Service inventory of Native American remains held by a DOE office, not marked |
| 6 | The place | no fault found | 0 | (19 rows name no place; their state names are Washington, DC addresses or a nationwide rule's examples) |
| 8 | The body | 80 of 80 | 0 | (BSEE, NPS, OSMRE and the Texas Governor read right) |
| 2 | A status | 80 of 80 held | (with class 5's nine) | a status follows the instrument; the nine rows of class 5 carry a status of the wrong instrument |

Also seen, not counted as a class: r60, a correction that replaces an effective date ("June 4, 2026" to read "This RG is effective on August 18, 2026"), keeps the replaced date beside the new one; three release pages (r2, r66, r70) are PDFs, which the connector never reads (a release is read from its feed's title and summary).

**What it says of the rules**: on actions never used to write them, the dates hold for 86% of the rows that state a step (98% on the first sample), the instrument for 89%, the figure for 83%; the places and bodies found no fault. The first sample's numbers were rules written to fit; these are the honest ones.

## The rows closed by later sessions

(Sessions 3140 to 3144 write their counts here.)
