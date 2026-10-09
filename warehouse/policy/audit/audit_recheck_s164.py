#!/usr/bin/env python3
"""Session 164: the audit of 100 policy actions, run again on the rows as they stand after session 157's recheck.

Energy Research Warehouse (ERW). Sessions 154 and 157 read 100 policy actions against their source documents and
wrote one finding a row and field (warehouse/policy/eval/audit_s154_findings.csv, audit_s157_findings.csv: the row's
value then, its class, the source's words). Session 157 then fixed the derived fields from each document's printed
text and reran the model fields. This tool reads the same 100 again, in the tables as they stand now, field by field,
and classes each. No request, no model call, no table written.

How a field is classed now, in this order:
    the same value     the row holds what it held when it was read: the finding stands, class and all;
    states             a changed value is set against the place the document names (audit_states_truth.csv, written by
                       session 157 from the two audits' reading): the same set of states is correct; a state the
                       document does not name is wrong; a state it names that the row lacks is missing;
    by code            a changed value code can settle: an abstract or a title that differs from the value read only
                       in white space and markup spacing (the class stands); a title that is now the printed
                       document's full title (correct); a date or a set of tags that is now the value the audit's
                       own trial of the fixed rule gave and the auditor counted as the mend (correct); a summary whose
                       first 500 characters are the 500 the audit recorded (the class stands); a score, which both
                       audits class a judgment against the rubric and never an error; a read's direction that now
                       claims none, a read's field that is now empty, a read's list that is the same set reordered;
    by reading         every other changed value was read again against the source's words by session 164's agent, as
                       the two audits were read, and its class and the words it rests on are in
                       warehouse/policy/eval/audit_s164_judgments.csv (event_id, field, cls, words). A changed value
                       with no line there is classed "not read again" and counted on its own line, never as correct.

Writes, under --out: recheck_findings.csv (one line a row and field: the value then, its class then, the value now, its
class now, how it was settled), recheck_table.md (errors before and now, field by field) and recheck_summary.json.
--worksheet prints the changed values that need reading.

    python warehouse/policy/audit/audit_recheck_s164.py --in-dir C:/Users/lossa/Documents/erw/warehouse/output \
        --out C:/Users/lossa/Documents/erw/runs/session164/audit
"""

import argparse
import csv
import json
import os
import re
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
EVAL = os.path.abspath(os.path.join(HERE, "..", "eval"))
FINDINGS = [("154", "audit_s154_findings.csv"), ("157", "audit_s157_findings.csv")]
TRUTH = "audit_states_truth.csv"
JUDGMENTS = "audit_s164_judgments.csv"
BAD = ["wrong", "missing", "not_in_source", "unsupported", "contradicted"]
GOOD = ["correct", "supported"]
NEUTRAL = ["judgment", "no_direction", "source_silent", "blank", "not_reachable"]
NOT_READ = "not read again"
CUT = 500   # the audits recorded a summary's first 500 characters
EXTRACTED = ["event_date", "agency", "action_type", "title", "abstract", "docket", "rin", "fr_document_number",
             "states", "source", "source_url", "related_urls", "status"]
MODEL = ["significance", "sector", "sector_tags", "why"]
READ = ["what_changes", "affected_sectors", "affected_isos", "affected_states", "direction_supply", "direction_demand",
        "direction_prices", "direction_buildout", "timeline", "plain_read"]
# The fields a model writes (the scorer and the reader). sector_tags is the connector's keyword rule, not a model's.
MODEL_MADE = ["significance", "sector", "why"] + READ


def read_events(path):
    with open(path, encoding="utf-8") as f:
        head = [ln for ln in f if ln.startswith("#")]
    return pd.read_csv(path, skiprows=len(head), dtype=str, keep_default_na=False)


def loose(s):
    """White space and the spacing of markup out of the way: what a change of cleaning alone leaves equal."""
    return re.sub(r"[^a-z0-9]+", "", str(s).lower())


def split(s):
    return sorted({x.strip() for x in str(s).split(";") if x.strip()})


def states_class(now, true):
    n, t = set(split(now)), set(split(true))
    if n == t:
        return "correct" if t else "source_silent"
    if n - t:
        return "wrong"
    return "missing"


def load(in_dir, judged=None):
    frames = []
    for sample, name in FINDINGS:
        f = pd.read_csv(os.path.join(EVAL, name), dtype=str, keep_default_na=False)
        f["sample"] = sample
        frames.append(f)
    finds = pd.concat(frames, ignore_index=True)
    with open(os.path.join(EVAL, TRUTH), encoding="utf-8", newline="") as f:
        truth = {r["event_id"]: r for r in csv.DictReader(f)}
    jp = os.path.join(EVAL, JUDGMENTS)
    if judged is None:   # the reading written down; a caller that classes from scratch passes its own (an empty one)
        judged = {}
        if os.path.exists(jp):
            with open(jp, encoding="utf-8", newline="") as f:
                for r in csv.DictReader(f):
                    judged[(r["event_id"], r["field"])] = r
    actions = read_events(os.path.join(in_dir, "policy_actions.csv")).set_index("event_id")
    reads = read_events(os.path.join(in_dir, "policy_reads.csv")).set_index("action_event_id")
    return finds, truth, judged, actions, reads


def settle(x, now, truth, judged):
    """(class now, how it was settled) for one finding and the row's value now."""
    then, cls, field = x["row_value"], x["cls"], x["field"]
    if now is None:
        return "not_reachable", "the row or its read is no longer in the table"
    if now == then:
        return cls, "the same value: the finding stands"
    if field == "states":
        t = truth.get(x["event_id"])
        if t is not None:
            return states_class(now, t["true_states"]), "set against the place the document names (audit_states_truth.csv)"
    j = judged.get((x["event_id"], field))
    if j is not None:
        return j["cls"], "read again by session 164's agent: " + j["words"]
    if field == "significance":
        return "judgment", "a score is a judgment against the rubric in both audits, never counted an error; the new score was not set against the rubric again"
    if field in ("abstract", "title") and loose(now) == loose(then):
        return cls, "differs from the value read only in white space or markup spacing: the finding stands"
    if field == "abstract" and len(then) == CUT and now.startswith(then) and cls in GOOD:
        return cls, f"the audit recorded the first {CUT} characters of the summary, and the row's value begins with them: the finding stands"
    if x["group"] == "read":
        if field.startswith("direction_"):
            if now in ("unclear", "none"):
                return "no_direction", "the read now claims no direction"
            if now == "":
                return "blank", "the read now holds no value for this field"
        elif now == "":
            return ("source_silent" if field.startswith("affected_") else "blank"), "the read now holds no value for this field"
        elif field.startswith("affected_") and split(now) == split(then):
            return cls, "the same set in another order: the finding stands"
    if field == "title":
        t = truth.get(x["event_id"])
        if t is not None and t.get("full_title") and loose(now) == loose(t["full_title"]):
            return "correct", "now the printed document's full title (audit_states_truth.csv)"
    if x.get("trial_value") and field in ("event_date", "sector_tags", "abstract", "title", "agency") and (
            split(now) == split(x["trial_value"]) if field == "sector_tags" else loose(now) == loose(x["trial_value"])):
        return "correct", "now the value the audit's own trial of the fixed rule gave"
    return NOT_READ, "changed since it was read, and not settled by code or by reading"


def run(in_dir, judged=None):
    finds, truth, judged, actions, reads = load(in_dir, judged)
    out = []
    for _, x in finds.iterrows():
        if x["group"] == "read":
            now = reads.loc[x["event_id"], x["field"]] if x["event_id"] in reads.index else None
        else:
            now = actions.loc[x["event_id"], x["field"]] if x["event_id"] in actions.index and x["field"] in actions.columns else None
        cls_now, how = settle(x, now, truth, judged)
        out.append({"sample": x["sample"], "draw": x["draw"], "event_id": x["event_id"], "group": x["group"], "field": x["field"],
                    "value_then": x["row_value"], "cls_then": x["cls"], "value_now": "" if now is None else now, "cls_now": cls_now,
                    "changed": "no" if now == x["row_value"] else "yes", "how": how, "source_words": x["source_words"],
                    "source_url": x["source_url"]})
    df = pd.DataFrame(out)
    recheck = {"actions": {}, "reads": {}}
    ids = sorted(set(finds["event_id"]))
    recheck["actions"] = actions.loc[[i for i in ids if i in actions.index], "model_recheck"].value_counts().to_dict()
    rids = sorted(set(finds.loc[finds["group"] == "read", "event_id"]))
    recheck["reads"] = reads.loc[[i for i in rids if i in reads.index], "recheck"].value_counts().to_dict()
    return df, recheck, actions, reads


def table(df):
    lines = ["| field | checked | errors before | errors now | fixed | new | still wrong | changed values | changed and not read again |",
             "|---|---|---|---|---|---|---|---|---|"]
    rows = []
    for group, fields in (("extracted", EXTRACTED), ("model", MODEL), ("read", READ)):
        for fld in fields:
            d = df[(df["group"] == group) & (df["field"] == fld)]
            before, now = d["cls_then"].isin(BAD), d["cls_now"].isin(BAD)
            r = {"field": fld + (" (read)" if group == "read" else ""), "checked": len(d), "before": int(before.sum()), "now": int(now.sum()),
                 "fixed": int((before & ~now & (d["cls_now"] != NOT_READ)).sum()), "new": int((~before & now).sum()),
                 "still": int((before & now).sum()), "changed": int((d["changed"] == "yes").sum()),
                 "not_read": int((d["cls_now"] == NOT_READ).sum())}
            rows.append(r)
            lines.append(f"| {r['field']} | {r['checked']} | {r['before']} | {r['now']} | {r['fixed']} | {r['new']} | {r['still']} | {r['changed']} | {r['not_read']} |")
    return lines, rows


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW policy audit: the 100 audited rows read again as they stand now")
    ap.add_argument("--in-dir", required=True)
    ap.add_argument("--out")
    ap.add_argument("--worksheet", action="store_true", help="print the changed values that need reading")
    a = ap.parse_args(argv)
    df, recheck, actions, reads = run(a.in_dir)
    if a.worksheet:
        need = df[df["cls_now"] == NOT_READ]
        for _, x in need.iterrows():
            act = actions.loc[x["event_id"]] if x["event_id"] in actions.index else None
            print(f"### {x['event_id']} | {x['field']} | then [{x['cls_then']}] {x['value_then'][:300]!r}")
            print(f"    now {x['value_now'][:500]!r}")
            if x["source_words"]:
                print(f"    audit's source words: {x['source_words'][:400]}")
            if act is not None and x["field"] in ("sector", "why", "significance", "sector_tags") + tuple(READ):
                print(f"    title: {act['title'][:200]} | agency {act['agency']} {act['action_type']} | sig {act['significance']} sector {act['sector']} tags {act['sector_tags']}")
                print(f"    text: {(act['abstract'] or act['first_paragraph'])[:600]}")
        print(f"{len(need)} values need reading")
        return 0
    lines, rows = table(df)
    checks = len(df)
    before = int(df["cls_then"].isin(BAD).sum())
    now = int(df["cls_now"].isin(BAD).sum())
    not_read = int((df["cls_now"] == NOT_READ).sum())
    rows_before = df[df["cls_then"].isin(BAD)]["event_id"].nunique()
    rows_now = df[df["cls_now"].isin(BAD)]["event_id"].nunique()
    made = df["field"].isin(MODEL_MADE)
    summary = {
        "checks": checks, "rows": int(df["event_id"].nunique()), "errors_before": before, "errors_now": now,
        "rows_with_an_error_before": int(rows_before), "rows_with_an_error_now": int(rows_now), "changed_not_read_again": not_read,
        "copied_or_rule_made": {"checks": int((~made).sum()), "errors_before": int(df[~made]["cls_then"].isin(BAD).sum()),
                                "errors_now": int(df[~made]["cls_now"].isin(BAD).sum())},
        "model_made": {"checks": int(made.sum()), "errors_before": int(df[made]["cls_then"].isin(BAD).sum()),
                       "errors_now": int(df[made]["cls_now"].isin(BAD).sum())},
        "model_recheck_of_the_100_actions": recheck["actions"], "recheck_of_their_reads": recheck["reads"], "by_field": rows,
    }
    tail = (f"{checks} checks on {summary['rows']} rows; errors before {before} in {rows_before} rows; errors now {now} in {rows_now} rows; "
            f"{not_read} changed values not read again (counted as neither).")
    print("\n".join(lines))
    print(tail)
    print(json.dumps({k: v for k, v in summary.items() if k != "by_field"}))
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        df.to_csv(os.path.join(a.out, "recheck_findings.csv"), index=False, lineterminator="\n")
        with open(os.path.join(a.out, "recheck_table.md"), "w", encoding="utf-8", newline="\n") as f:
            f.write("\n".join(lines) + "\n\n" + tail + "\n")
        with open(os.path.join(a.out, "recheck_summary.json"), "w", encoding="utf-8", newline="\n") as f:
            json.dump(summary, f, indent=1)
    return 0


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.exit(main())
