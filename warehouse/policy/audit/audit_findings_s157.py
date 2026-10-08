#!/usr/bin/env python3
"""Session 157: what a person read in the second 50 source documents (seed 157), for the fields code cannot settle.

Energy Research Warehouse (ERW). The same standards and the same classes as audit_findings.py (session 154), which
this module does not replace: keys are the draw numbers of runs/session157/audit/sample.csv
(warehouse/policy/eval/audit_s157_sample.csv). Every class can be checked by a second person against the saved
document: the source's words are quoted.

Classes of an extracted field: correct, wrong, missing, not_in_source, source_silent.
Classes of a model field: supported, unsupported, contradicted, judgment, blank, no_direction.

TRUE_STATES_154 and TRUE_STATES give the place as two-letter codes for both samples (audit_truth.py writes
warehouse/policy/eval/audit_states_truth.csv from them): the states where the project, plant or plan the action
concerns is, as the document says it; "" where the document names none.
"""

# Session 154's 50, from its own findings (audit_findings.py STATES) and the documents it saved: the codes of the
# states its quoted words name. Draw 7 keeps session 154's ruling (VA: the licensee's name is the only place the
# document names the state, and the two plants are in it). Draw 47 is a list of licence amendments at plants in
# several states whose title and summary name none: session 154 classed it source_silent, so "".
TRUE_STATES_154 = {
    1: "", 2: "", 3: "PA", 4: "", 5: "", 6: "", 7: "VA", 8: "TX", 9: "", 10: "CA", 11: "TX", 12: "LA;TX", 13: "WV",
    14: "AZ", 15: "ID;WA", 16: "", 17: "LA;MS", 18: "", 19: "WA", 20: "NY", 21: "CA;NM", 22: "KY", 23: "NY",
    24: "AR;TX", 25: "NY", 26: "", 27: "TX", 28: "AL", 29: "MN", 30: "NH", 31: "", 32: "LA;TX", 33: "", 34: "CA",
    35: "MI", 36: "AK", 37: "", 38: "OH", 39: "", 40: "TN", 41: "WI", 42: "", 43: "", 44: "AK", 45: "", 46: "MN",
    47: "", 48: "", 49: "", 50: "",
}
