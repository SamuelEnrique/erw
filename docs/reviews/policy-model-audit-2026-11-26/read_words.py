"""Session 10217: each words branch's new sentences, looked for in what the site's own code drew (draw_policy.mjs and
draw_note.mjs outputs). Prints pass or fail a sentence.
    python runs/c10217/read_words.py <draw text, open> <draw text, Texas> <note text>
"""
import sys

open_t = open(sys.argv[1], encoding="utf-8").read()
tx_t = open(sys.argv[2], encoding="utf-8").read()
note_t = open(sys.argv[3], encoding="utf-8").read()
CHECKS = [
    ("1", open_t, "Steps on records scored below significance 5, or not scored at all (the newest documents, and the grid operators' and FERC's large-load orders, which are never scored); this lifts the floor, the other filters kept."),
    ("1", open_t, "A record not scored (the newest documents, and the grid operators' and FERC's large-load orders, which are never scored) is below every floor: it is shown only with Significance set to All."),
    ("2", open_t, "Records whose newest document is dated from 2026-11-18 to 2026-11-25, both days counted (eight calendar days, ending on the day of the file's newest document; data/policy/monitor.json, built 2026-11-25); this page's day is 2026-11-26."),
    ("2", note_t, "the actions of the past week (from seven days before the day to the day, both counted: eight calendar days; audit of 26 November 2026, finding 4)"),
    ("3", tx_t, "The utilities' own large-load rules: 11 in TX (13 changes in the 90 days to 13 November 2026) , on What a datacenter pays."),
    ("3", note_t, "the count of changes in the 90 days to 13 November 2026 (every change of utility_large_load_rule_changes , whose window ends that day"),
    ("4", note_t, "a rule is \"effective\" only when its effective date is on or before the document's own date, and a rule whose effective date comes later stays \"final\", on the page too, after that date has passed"),
    ("5", note_t, "Since session 1876 (policy faults row 28) that table adds nothing: for each month of a record's newest document and each unit, it counts the records stating a figure in that unit and shows the largest, with its record"),
    ("5", note_t, "is no longer drawn, and the check of a sum stays for an older file's keys"),
    ("6", open_t, "Signed into law, as the ERW's read of the text marked it; the read did not mark it in effect. Where the text prints when it takes effect, the Effective column or the status's cite says so, and that day may already have passed."),
]
bad = 0
for b, t, s in CHECKS:
    ok = s in t
    bad += not ok
    print(f"{'pass' if ok else 'FAIL'} wip/audit-policy-{b}: {s[:110]}")
print(f"{len(CHECKS) - bad} of {len(CHECKS)} drawn")
