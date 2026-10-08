#!/usr/bin/env python3
"""Session 154: the error rate by field, from the checks by code (auto_checks.csv) and by reading (audit_findings.py).

Energy Research Warehouse (ERW). Writes, under --out: findings.csv (one line per row and field, with its class and
both texts), errors.csv (the lines that are errors) and error_table.md (the table of the report). No request, no
model call, no table written.

    python warehouse/policy/audit/audit_table.py --in-dir C:/Users/lossa/Documents/erw/warehouse/output --out <audit>
"""

import argparse
import csv
import os
import sys

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import audit_findings as F  # noqa: E402

EXTRACTED = ["event_date", "agency", "action_type", "title", "abstract", "docket", "rin", "fr_document_number",
             "states", "source", "source_url", "related_urls", "status"]
MODEL = ["significance", "sector", "sector_tags", "why"]
READ = ["what_changes", "affected_sectors", "affected_isos", "affected_states", "direction_supply", "direction_demand",
        "direction_prices", "direction_buildout", "timeline", "plain_read"]
GOOD = {"correct", "supported"}
BAD = ["wrong", "missing", "not_in_source", "unsupported", "contradicted"]
NEUTRAL = ["judgment", "no_direction", "source_silent", "blank", "not_reachable"]


def read_events(path):
    with open(path, encoding="utf-8") as f:
        head = [ln for ln in f if ln.startswith("#")]
    return pd.read_csv(path, skiprows=len(head), dtype=str, keep_default_na=False)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW policy audit: the error table")
    ap.add_argument("--in-dir", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args(argv)
    acts = read_events(os.path.join(args.in_dir, "policy_actions.csv")).set_index("event_id")
    reads = read_events(os.path.join(args.in_dir, "policy_reads.csv")).set_index("action_event_id")
    with open(os.path.join(args.out, "sample.csv"), encoding="utf-8") as f:
        sample = [r["event_id"] for r in csv.DictReader(ln for ln in f if not ln.startswith("#"))]
    auto = {(r["event_id"], r["field"]): r for r in csv.DictReader(open(os.path.join(args.out, "auto_checks.csv"),
                                                                        encoding="utf-8"))}
    trial = {}
    tpath = os.path.join(args.out, "trial", "changes.csv")
    if os.path.exists(tpath):
        trial = {(r["event_id"], r["field"]): r["trial"] for r in csv.DictReader(open(tpath, encoding="utf-8"))}
    out = []

    def add(n, eid, group, field, cls, row_value, source_words, note=""):
        fixed = trial.get((eid, "parties" if field == "agency" else field), "")
        out.append(dict(draw=n, event_id=eid, group=group, field=field, cls=cls, row_value=str(row_value)[:500],
                        source_words=source_words[:700], note=note, trial_value=fixed if cls in BAD else "",
                        source_url=acts.at[eid, "source_url"]))

    for n, eid in enumerate(sample, 1):
        r = acts.loc[eid]
        news = r.action_type == "press_release"
        for fld in EXTRACTED:
            a = auto.get((eid, fld))
            if (n, fld) in F.OVERRIDES:
                cls, words = F.OVERRIDES[(n, fld)]
                add(n, eid, "extracted", fld, cls, r[fld], words)
            elif fld == "states":
                cls, words = F.STATES[n]
                add(n, eid, "extracted", fld, cls, r.states, words, a["note"] if a else "")
            elif fld == "source":
                add(n, eid, "extracted", fld, "correct", r.source, "the feed, list or API the row's address is of")
            elif fld == "related_urls":
                add(n, eid, "extracted", fld, "source_silent" if not r.related_urls else "judgment", r.related_urls,
                    "blank in the row; the document cannot say whether a release reports it")
            elif news and fld == "agency":
                add(n, eid, "extracted", fld, "correct", r.agency, F.NEWS_AGENCY_OK[n])
            elif news and fld == "action_type":
                add(n, eid, "extracted", fld, "correct", r.action_type, "a news release or news item of the agency's site")
            elif news and fld == "status":
                add(n, eid, "extracted", fld, "source_silent", r.status, "the connector's constant for a news row")
            elif a and a["cls"] != "to_read":
                add(n, eid, "extracted", fld, a["cls"], r[fld], a["source_value"], a["note"])
            else:
                raise RuntimeError(f"no class for {eid} {fld}")
        # the keyword tags and the scorer's three fields
        if n in F.TAGS_MISSING:
            add(n, eid, "model", "sector_tags", "missing", r.sector_tags, F.TAGS_MISSING[n])
        elif n in F.TAGS_WRONG:
            add(n, eid, "model", "sector_tags", "not_in_source", r.sector_tags, F.TAGS_WRONG[n])
        elif n in F.TAGS_SILENT:
            add(n, eid, "model", "sector_tags", "source_silent", r.sector_tags, F.TAGS_SILENT[n])
        else:
            add(n, eid, "model", "sector_tags", "supported", r.sector_tags, "each tag's keyword is in the title or summary")
        add(n, eid, "model", "significance", "judgment", r.significance,
            F.SIGNIFICANCE_FLAGS.get(n, "follows the rubric's bands"), F.SIGNIFICANCE_NOTES.get(n, ""))
        if n in F.SECTOR_UNSUPPORTED:
            add(n, eid, "model", "sector", "unsupported", r.sector, F.SECTOR_UNSUPPORTED[n][1])
        else:
            add(n, eid, "model", "sector", "supported", r.sector, "")
        if n in F.WHY_UNSUPPORTED:
            assert F.WHY_UNSUPPORTED[n][0] == r.why, (n, r.why)
            add(n, eid, "model", "why", "unsupported", r.why, F.WHY_UNSUPPORTED[n][1])
        else:
            add(n, eid, "model", "why", "supported", r.why, "")
        if eid in reads.index:
            x = reads.loc[eid]
            for fld in READ:
                cls, words, src = F.READS[n][fld]
                held = x[fld]
                assert (held == "") == (cls in ("blank", "source_silent") and not words), (n, fld, held, cls)
                if words and fld not in ("timeline", "plain_read", "what_changes"):
                    assert words == held, (n, fld, words, held)
                add(n, eid, "read", fld, cls, held, src)
    df = pd.DataFrame(out)
    df.to_csv(os.path.join(args.out, "findings.csv"), index=False, lineterminator="\n")
    df[df["cls"].isin(BAD)].to_csv(os.path.join(args.out, "errors.csv"), index=False, lineterminator="\n")
    lines = ["| field | rows checked | correct or supported | wrong | missing | not in source | unsupported | "
             "contradicted | judgment or no direction claimed | source silent, blank or not applicable | not reachable | "
             "errors of rows checked | errors of rows where the source or the row states the field |",
             "|---|---|---|---|---|---|---|---|---|---|---|---|---|"]
    for group, fields in (("extracted", EXTRACTED), ("model", MODEL), ("read", READ)):
        for fld in fields:
            d = df[(df["group"] == group) & (df["field"] == fld)]
            c = d["cls"].value_counts().to_dict()
            good = sum(c.get(k, 0) for k in GOOD)
            bad = sum(c.get(k, 0) for k in BAD)
            states = good + bad
            rate = lambda a, b: f"{a} of {b} ({100 * a / b:.0f}%)" if b else "0 of 0"
            lines.append(f"| {fld}{' (read)' if group == 'read' else ''} | {len(d)} | {good} | {c.get('wrong', 0)} | "
                         f"{c.get('missing', 0)} | {c.get('not_in_source', 0)} | {c.get('unsupported', 0)} | "
                         f"{c.get('contradicted', 0)} | {c.get('judgment', 0) + c.get('no_direction', 0)} | "
                         f"{c.get('source_silent', 0) + c.get('blank', 0)} | {c.get('not_reachable', 0)} | "
                         f"{rate(bad, len(d))} | {rate(bad, states)} |")
    with open(os.path.join(args.out, "error_table.md"), "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    bad = df[df["cls"].isin(BAD)]
    print(f"\n{len(df)} checks on {len(sample)} rows ({int(df['group'].eq('read').sum())} on "
          f"{df[df['group'] == 'read']['event_id'].nunique()} impact reads); {len(bad)} errors in "
          f"{bad['event_id'].nunique()} rows; {int((bad['trial_value'] != '').sum())} of them changed by the trial")
    print(bad.groupby(["group", "field", "cls"]).size().to_string())
    ext = bad[bad["group"] == "extracted"]
    print(f"rows with an error in an extracted field: {ext['event_id'].nunique()}; in a field of the scorer or the tags: "
          f"{bad[bad['group'] == 'model']['event_id'].nunique()}; reads with an error: "
          f"{bad[bad['group'] == 'read']['event_id'].nunique()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
