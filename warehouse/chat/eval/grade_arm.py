#!/usr/bin/env python3
"""Session 5272 (chain 256): an arm of a measure graded, a run that is not one of a set's stored runs.

Energy Research Warehouse (ERW). eval_site.py grades the runs of a set, the files eval_s<N>_site_<set>_run.json, and a
question's newest answer among them is the set's score. An asking made to measure a variant (another effort, a prompt
with a rule taken out) must not stand as a question's newest answer, so it is kept under another name and listed in
runs.json under left_out. This grades such a file the same way: the same keys, the same rules, a held table's results
struck out first, and the calls made after the figure by class.

    python warehouse/chat/eval/grade_arm.py --run eval_s5272_site_platform_ten_rules_run.json [--set platform] [--rules 5251]

Writes <the run's name>_grades.json beside it (the run's `_run.json` replaced by `_grades.json`) and prints the counts.
No model, no network.
"""
import importlib.util
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def grade(run_name, which="platform", how="5251", here=HERE):
    """(the grades document, the measure of the calls after the figure) of one run file of the folder."""
    S = module("eval_site_for_arm", os.path.join(HERE, "eval_site.py"))
    E = module("eval_s1113_for_arm", os.path.join(HERE, "eval_s1113.py"))
    P = module("platform_scores_for_arm", os.path.join(HERE, "platform_scores.py"))
    C = module("calls_after_for_arm", os.path.join(HERE, "calls_after.py"))
    if not run_name.endswith("_run.json"):
        raise SystemExit("--run is a file of this folder whose name ends _run.json")
    if S.sessions_of(which, here) and os.path.basename(run_name) in {os.path.basename(S.files(s, which, here)["run"]) for s in S.sessions_of(which, here)}:
        raise SystemExit(f"{run_name} is one of the set's own runs: eval_site.py grades it")
    run_path, grades_path = os.path.join(here, run_name), os.path.join(here, run_name[:-len("_run.json")] + "_grades.json")
    rules = {"none": (), "2223": E.G.RULES_2223, "5201": E.G.RULES_5201, "5251": E.G.RULES_5251}[how]
    qs = E.questions(E.SETS[which]["questions"])
    sys.path.insert(0, os.path.dirname(HERE))
    import license_hold
    doc_run = S.read_json(run_path)
    if S.redact_held(doc_run, license_hold.license_needed):
        S.write_json(run_path, doc_run)
        print("a result of a held or paused grid's own table was struck out")
    keep = dict(E.SETS[which])
    try:
        E.SETS[which]["run"], E.SETS[which]["grades"] = run_path, grades_path
        doc = E.grade_set(which, rules)
    finally:
        E.SETS[which].update(keep)
    doc["loop"] = "site"
    doc["cost_usd"] = round(S.spent(run_path)[0], 4)
    doc["arm"] = "an arm of a measure, not one of the set's runs (runs.json, left_out)"
    doc.update(S.counts(doc["questions"], qs))
    S.write_json(grades_path, doc)
    m = C.measure(qs, [("arm", doc_run["questions"], {}, [])], lambda q, rec: P.in_hand(q, rec, E.G))
    return doc, m


def main(argv):
    def val(name, default=None):
        return argv[argv.index(name) + 1] if name in argv else default
    doc, m = grade(val("--run"), val("--set", "platform"), val("--rules", "5251"))
    rows = doc["questions"]
    print(f"right {sum(1 for r in rows if r['ok'])} of {len(rows)}; cost USD {doc['cost_usd']:.4f}; not right: " + (", ".join(r["id"] for r in rows if not r["ok"]) or "none"))
    C = module("calls_after_for_arm_lines", os.path.join(HERE, "calls_after.py"))
    print("\n".join(C.lines(m)))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
