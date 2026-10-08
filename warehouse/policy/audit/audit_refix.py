#!/usr/bin/env python3
"""Session 154: trial of the fixed extraction rules of policy_sources.py over the held table. No request, no model
call, and nothing written outside --out-dir.

Energy Research Warehouse (ERW). The connector keeps no raw copy of the Register's records on this machine (the table
came back from the Redivis draft; warehouse/raw/policy_sources does not exist), so the fixed rules are applied to what
the table itself holds, field by field, and compared with the table:

  states        the old rule and the fixed rule are both run on the row's own title and abstract; a state the old rule
                gives and the fixed rule does not is taken out of the row (West Virginia read as Virginia; Washington,
                DC read as the state). The Register's topics and the abstract past 1,500 characters are not in the
                table, so a row whose topics name the state would keep it in a real run: the count is an upper bound.
  sector_tags   the fixed rule's additions and removals depend on the agency, the docket and the text: FERC CP and PF
                dockets gain gas and lose transmission; FERC Project No. and DI dockets gain power and renewables;
                every NRC row gains nuclear and loses storage unless its text speaks of batteries or energy storage.
  event_date    NRC and DOE news rows whose link is in a saved feed (--feed NAME=path): the day in US Eastern time,
                not the UTC day. Rows no longer in a feed cannot be recomputed and are counted on their own line.
  parties       a release of the Governor's office listed by the PUCT (gov.texas.gov) names its issuer.
  abstract      NOT recomputed: the fix is in how the Register's markup is cleaned, and the table holds only the
                cleaned text. The rows whose abstract shows the fault ("NO X", "CO 2", "PM 2.5") are counted.

    python warehouse/policy/audit/audit_refix.py --in-dir C:/Users/lossa/Documents/erw/warehouse/output \
        --out-dir C:/Users/lossa/Documents/erw/runs/session154/audit/trial \
        --feed nrc=<audit>/raw/nrc_feed.extra.html --feed doe=<audit>/raw/doe_feed.extra.html
"""

import argparse
import csv
import os
import re
import sys
import xml.etree.ElementTree as ET

import pandas as pd

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..", "..", "connectors")))

SPLIT = re.compile(r"\b(?:NO|SO|CO|PM|CH|SF|UF|O|H|N) (?:X|x|\d+(?:\.\d+)?)(?= |\)|,|\.)")


def old_states(ps, text):
    """The rule as it stood before session 154."""
    return {c for n, c in ps.STATES.items() if re.search(rf"\b{n}\b", text)}


def main(argv=None):
    import policy_sources as ps
    ap = argparse.ArgumentParser(description="ERW policy audit: trial of the fixed rules over the held table")
    ap.add_argument("--in-dir", required=True)
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--feed", action="append", default=[], help="NAME=path of a saved feed (nrc, doe)")
    args = ap.parse_args(argv)
    src = os.path.join(args.in_dir, "policy_actions.csv")
    if os.path.abspath(args.out_dir) == os.path.abspath(args.in_dir):
        print("--out-dir must not be the table's own directory", file=sys.stderr)
        return 2
    with open(src, encoding="utf-8") as f:
        head = [ln for ln in f if ln.startswith("#")]
    df = pd.read_csv(src, skiprows=len(head), dtype=str, keep_default_na=False)
    new = df.copy()
    days = {}
    for item in args.feed:
        name, path = item.split("=", 1)
        for it in ET.fromstring(open(path, "rb").read()).iter("item"):
            link, day = (it.findtext("link") or "").strip(), ps.release_day(it.findtext("pubDate"))
            if link and day:
                days[(name, link)] = day
    changes, notes = [], {"news rows not in a saved feed (event_date not recomputed)": 0,
                          "abstracts that show split markup (not recomputed)": 0}
    for i, r in df.iterrows():
        text = f"{r.title} {r.abstract}"
        fr = r.source == "federalregister:api"
        # states
        if fr or r.agency in ("NRC", "DOE"):
            gone = old_states(ps, text) - set(x for x in ps.states(text).split(";") if x)
            held = [x for x in r.states.split(";") if x]
            kept = ";".join(x for x in held if x not in gone)
            if kept != r.states:
                new.at[i, "states"] = kept
        # sector_tags
        held = {x for x in r.sector_tags.split(";") if x}
        got = set(held)
        if r.agency == "FERC" and ps.GAS_DOCKET.search(r.docket):
            got = (got | {"gas"}) - {"transmission"}
        if r.agency == "FERC" and ps.HYDRO_DOCKET.search(r.docket):
            got |= {"power", "renewables"}
        if r.agency == "NRC":
            got.add("nuclear")
            if not ps.NRC_STORAGE.search(text):
                got.discard("storage")
        if got != held:
            new.at[i, "sector_tags"] = ";".join(t for t, _ in ps.SECTOR_TAGS if t in got)
        # event_date of feed rows
        name = r.source.split(":")[0]
        if r.source in ("nrc:news", "doe:news"):
            day = days.get((name, r.source_url))
            if day is None:
                notes["news rows not in a saved feed (event_date not recomputed)"] += 1
            elif day != r.event_date:
                new.at[i, "event_date"] = day
        # parties
        if r.action_type == "press_release" and "gov.texas.gov" in r.source_url.lower() and "Governor" not in r.parties:
            new.at[i, "parties"] = f"Office of the Texas Governor;{r.agency}"
        if SPLIT.search(r.abstract):
            notes["abstracts that show split markup (not recomputed)"] += 1
        for c in ("states", "sector_tags", "event_date", "parties"):
            if new.at[i, c] != r[c]:
                changes.append(dict(event_id=r.event_id, agency=r.agency, action_type=r.action_type, field=c,
                                    held=r[c], trial=new.at[i, c], title=r.title[:120]))
    os.makedirs(args.out_dir, exist_ok=True)
    out = os.path.join(args.out_dir, "policy_actions.csv")
    with open(out, "w", encoding="utf-8", newline="") as f:
        f.writelines(head)
        f.write("# TRIAL of session 154 (warehouse/policy/audit/audit_refix.py): the fixed rules of policy_sources.py applied "
                "to the held rows; not the table of record.\n")
        new.to_csv(f, index=False, lineterminator="\n")
    with open(os.path.join(args.out_dir, "changes.csv"), "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["event_id", "agency", "action_type", "field", "held", "trial", "title"],
                           lineterminator="\n")
        w.writeheader()
        w.writerows(changes)
    c = pd.DataFrame(changes)
    rows = c["event_id"].nunique() if len(c) else 0
    print(f"{len(df)} rows held; {rows} rows change in at least one field; {len(c)} field changes")
    if len(c):
        print(c.groupby("field")["event_id"].nunique().to_string())
        print(c.groupby(["field", "agency"])["event_id"].nunique().to_string())
    for k, v in notes.items():
        print(f"{k}: {v}")
    same = [col for col in df.columns if col not in ("states", "sector_tags", "event_date", "parties")
            and not (new[col] == df[col]).all()]
    print(f"other columns changed: {same or 'none'}; rows in the trial table: {len(new)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
