#!/usr/bin/env python3
"""The policy monitor's site files: what the "What changed this week" view of /policy reads beside the live set
(session 157).

Energy Research Warehouse (ERW). No warehouse table is written, no request is made, no model is called and nothing
is loaded: this reads tables already built and the rule and feed files, and writes five files under
site/data/policy/, each whole, by rename. Method: docs/methods/policy_monitor.md.

    python warehouse/derived/policy_monitor_site.py --in-dir TRIAL --in-dir C:/.../warehouse/output
    python warehouse/derived/policy_monitor_site.py --in-dir ... --out-dir DIR        # a trial: the files under DIR
    python warehouse/derived/policy_monitor_site.py --in-dir ... --last-run FILE      # the refresh step's last run
    python warehouse/derived/policy_monitor_site.py --in-dir ... --cases FIXTURE --cases-full FILE
                                                    # also the tag cases both the Python and the page's rule are held to
    python warehouse/derived/policy_monitor_site.py --daily
                                                    # the daily run's soft step, after policy_monitor_refresh: the three
                                                    # files that follow the tables (state_rules, refresh, action_tags)

The daily step never writes a thinner file. The tables are read from warehouse/output; on a machine without the
three large-load tables (GitHub's runner) each is first rebuilt from the ERW's archive, and if one is still missing
nothing is written (a skip, with the reason). A state file with fewer rows, or fewer reads, than the one held is not
written (the step fails and says so). action_tags.json is written only from a policy_actions that has the column
first_paragraph. A file whose content is the same apart from its build time and day is left as it is, so a day with
nothing new commits nothing. No live page (/cost-of-power/battery, /network, /storage) reads any of these files.

The files (the first --in-dir that holds a table wins):
    tag_rules.json     a byte-for-byte copy of warehouse/config/policy_tag_rules.json: the page applies the same rule
                       to the rows it reads from the live set, so an action is tagged the day it arrives
    action_tags.json   the tags the Python rule gives on policy_actions as held, and, for an action tagged from its
                       first paragraph, that paragraph (the live set does not hold it until the table is next loaded)
    grids.json         the names by which a document's own words name a grid operator (rules_in_motion.OPERATOR_WORDS)
                       and MISO's fixed words
    state_rules.json   every row of large_load_rules (public) and large_load_rules_internal, flat, newest first, with
                       the grids it is under by the written rule of warehouse/derived/rules_in_motion.py. A row of the
                       internal table carries its facts, its link and the model's read: never its sentence or its
                       worded status (the sentence rule of session 154)
    refresh.json       warehouse/config/policy_monitor_feeds.json (each regulator, its open list, whether the daily
                       step asks it and, if not, the exact reason) with the facts of the step's last run

Never in a file: anything municipal (a row whose shown words hold one of rules_in_motion.MUNICIPAL_WORDS is kept out
and counted), a filled field, an em dash.
"""

import argparse
import datetime as dt
import json
import os
import random
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(ROOT, "warehouse", "connectors"))
import policy_action_tags as pat  # noqa: E402
import rules_in_motion as rim  # noqa: E402

SITE_DIR = os.path.join(ROOT, "site", "data", "policy")
RULES = os.path.join(ROOT, "warehouse", "config", "policy_tag_rules.json")
FEEDS = os.path.join(ROOT, "warehouse", "config", "policy_monitor_feeds.json")
TOPICS = ["large-load interconnection", "large-load tariff", "transmission cost allocation", "interconnection reform"]
EM = chr(0x2014)
CASES_SEED, CASES_OTHERS = 157, 200
CASE_FIELDS = ["event_id", "agency", "action_type", "title", "abstract", "first_paragraph", "docket"]


def now_iso():
    return dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")


def same_but_time(path, obj):
    """True when the file held has the content of obj apart from built_at_utc and as_of."""
    if not os.path.exists(path):
        return False
    try:
        with open(path, encoding="utf-8") as f:
            old = json.load(f)
    except ValueError:
        return False
    strip = lambda d: {k: v for k, v in d.items() if k not in ("built_at_utc", "as_of")}
    return isinstance(old, dict) and strip(old) == strip(json.loads(json.dumps(obj)))


def write_whole(path, obj, keep_if_same=False):
    if keep_if_same and same_but_time(path, obj):
        return False
    os.makedirs(os.path.dirname(path), exist_ok=True)
    text = json.dumps(obj, indent=1, ensure_ascii=False) + "\n"
    if EM in text:
        raise RuntimeError(f"{path}: an em dash, which no file of this repository holds; nothing is written")
    with open(path + ".tmp", "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    os.replace(path + ".tmp", path)
    return True


DAILY_TABLES = ["large_load_rules", "large_load_rules_internal", "large_load_rule_reads"]


def daily(out_dir, today, in_dirs=None, last_run=None):
    """The daily run's soft step (see the module's note): returns the exit code. in_dirs (a trial, a test): the
    tables are read from there and nothing is rebuilt from the archive."""
    import subprocess
    import iso_prices as ip
    skip = int(os.environ.get("ERW_SKIP_EXIT", "75"))
    held = lambda t: rim.find(t, in_dirs) if in_dirs else (os.path.join(ip.OUT_DIR, t + ".csv") if os.path.exists(os.path.join(ip.OUT_DIR, t + ".csv")) else None)
    for t in DAILY_TABLES:
        path = os.path.join(ip.OUT_DIR, t + ".csv")
        if not in_dirs and not os.path.exists(path):
            print(f"policy_monitor_site: {t} is not on this machine; rebuilding it from the archive (erw-archive)")
            r = subprocess.run([sys.executable, os.path.join(ROOT, "warehouse", "archive", "restore.py"), t, "--from-bucket",
                                "--out", path], cwd=ROOT)
            if r.returncode != 0 and os.path.exists(path):
                os.remove(path)   # a rebuild that did not finish is not an input
    missing = [t for t in DAILY_TABLES if not held(t)]
    if missing:
        print(f"policy_monitor_site SKIPPED: {', '.join(missing)} not on this machine and not rebuilt from the archive; "
              "no file is written (a thinner file is never written)")
        return skip
    dirs, rules, done = (in_dirs or [ip.OUT_DIR]), pat.load_rules(RULES), []
    obj = state_rules(dirs, today)
    path = os.path.join(out_dir, "state_rules.json")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            old = json.load(f)
        was, now = len(old["rows"]), len(obj["rows"])
        was_r, now_r = sum(1 for r in old["rows"] if r.get("read")), sum(1 for r in obj["rows"] if r.get("read"))
        if now < was or now_r < was_r:
            raise RuntimeError(f"state_rules.json would be thinner ({now} rows, {now_r} with a read) than the file held "
                               f"({was} rows, {was_r} with a read); nothing is written")
    done.append(f"state_rules.json ({len(obj['rows'])} rows): "
                + ("written" if write_whole(path, obj, keep_if_same=True) else "unchanged, left as it is"))
    obj = refresh_file(last_run or os.path.join(ip.RAW_DIR, "policy_monitor_refresh", "last_run.json"))
    if obj is not None:
        done.append("refresh.json: " + ("written" if write_whole(os.path.join(out_dir, "refresh.json"), obj, keep_if_same=True)
                                        else "unchanged, left as it is"))
    apath = rim.find("policy_actions", dirs)
    if apath and "first_paragraph" in pat.read_events(apath).columns:
        obj, _ = action_tags(dirs, rules)
        done.append(f"action_tags.json ({obj['actions_tagged']} of {obj['actions_read']} actions tagged): "
                    + ("written" if write_whole(os.path.join(out_dir, "action_tags.json"), obj, keep_if_same=True)
                       else "unchanged, left as it is"))
    else:
        done.append("action_tags.json left as it is: policy_actions is not on this machine or has no first_paragraph yet")
    for d in done:
        print("policy_monitor_site:", d)
    return 0


def copy_rules(out_dir):
    with open(RULES, "rb") as f:
        raw = f.read()
    os.makedirs(out_dir, exist_ok=True)
    with open(os.path.join(out_dir, "tag_rules.json.tmp"), "wb") as f:
        f.write(raw)
    os.replace(os.path.join(out_dir, "tag_rules.json.tmp"), os.path.join(out_dir, "tag_rules.json"))


def grids_file():
    return {"grids": [{"key": g, "name": rim.GRID_NAMES[g], "words": rim.OPERATOR_WORDS[g]} for g in rim.GRIDS],
            "paused": {"miso": rim.MISO_WORDS},
            "rule": "A federal action is under a grid when one of the grid's words stands in its title, abstract or "
                    "first paragraph as a whole word (a word holding a space in any case, a single word in its own "
                    "case), or when a docket listed in tag_rules.json that tagged it names the grid. An action that "
                    "names no operator is under every grid but MISO. MISO shows its fixed words and no row."}


def action_tags(dirs, rules):
    path = rim.find("policy_actions", dirs)
    if not path:
        return None, None
    acts = pat.read_events(path)
    if "first_paragraph" not in acts.columns:
        acts["first_paragraph"] = ""
    tags, paras, counts = {}, {}, {t: 0 for t in rules["tags"]}
    rows = acts.to_dict("records")
    for r in rows:
        hits = pat.tag_action(r, rules)
        if hits:
            tags[r["event_id"]] = hits
            for h in hits:
                counts[h["tag"]] += 1
            if any(h["matched_field"] == "first_paragraph" for h in hits):
                paras[r["event_id"]] = r["first_paragraph"]
    obj = {"built_at_utc": now_iso(), "rule_version": str(rules["version"]), "actions_read": len(rows),
           "actions_tagged": len(tags), "fields_read": rules["fields_matched"], "counts": counts, "tags": tags,
           "first_paragraph": paras}
    return obj, rows


def near_miss(row, rules):
    """True when a matched field of the row holds any term of the rule (so an exclusion, the scope or the municipal
    rule is what keeps it untagged)."""
    for f in rules["fields_matched"]:
        t = pat.norm(row.get(f, ""))
        if not t:
            continue
        for spec in rules["tags"].values():
            if any(pat.has(x["term"], t) for x in spec["terms"]):
                return True
    return False


def cases(rows, rules):
    """(the fixture's cases, every row as a case): each with the fields the rule reads and what the Python rule gives."""
    full = [dict({k: r.get(k, "") for k in CASE_FIELDS}, expect=pat.tag_action(r, rules)) for r in rows]
    tagged = [c for c in full if c["expect"]]
    by = {r["event_id"]: r for r in rows}
    near = [c for c in full if not c["expect"] and near_miss(by[c["event_id"]], rules)]
    have = {c["event_id"] for c in tagged + near}
    others = sorted(c["event_id"] for c in full if c["event_id"] not in have)
    pick = set(random.Random(CASES_SEED).sample(others, min(CASES_OTHERS, len(others))))
    keep = tagged + near + [c for c in full if c["event_id"] in pick]
    return sorted(keep, key=lambda c: c["event_id"]), full


def state_rules(dirs, today):
    cutoff = rim.months_back(today, rim.WINDOW_MONTHS)
    notes, off = [], {}
    rows, _ = rim.table_rows(dirs, cutoff, notes, every=True)
    kept, seen = [], set()
    for r in rows:
        if rim.municipal(r):
            k = "a row that holds a word the monitor never shows (" + ", ".join(rim.MUNICIPAL_WORDS) + "): in the table, not in the file"
            off[k] = off.get(k, 0) + 1
            continue
        if any(EM in str(r.get(k) or "") for k in ("title", "sentence", "status_as_worded", "read", "docket")):
            k = "a row whose own words hold an em dash, which no file of this repository holds: in the table, not in the file"
            off[k] = off.get(k, 0) + 1
            continue
        if r["id"] in seen:
            continue
        seen.add(r["id"])
        kept.append(r)
    moving = {r["id"]: r.pop("in_motion") for r in kept}
    grids, federal, nowhere = rim.place([dict(r) for r in kept])
    where = {}
    for g in rim.GRIDS:
        for r in grids[g]:
            w = where.setdefault(r["id"], {"row": r, "grids": [], "all": False, "why": r.get("why_here")})
            w["grids"].append(g)
    for r in federal:
        where[r["id"]] = {"row": r, "grids": [], "all": True, "why": r.get("why_here")}
    for r, why in nowhere:
        where.setdefault(r["id"], {"row": r, "grids": [], "all": False, "why": "On no grid of the page: " + why})
    feeds = {}
    if os.path.exists(FEEDS):
        with open(FEEDS, encoding="utf-8") as f:
            feeds = {x["regulator"]: x["key"] for x in json.load(f)["regulators"]}
    out = []
    for r in kept:
        w = where[r["id"]]
        row = {k: v for k, v in w["row"].items() if k not in ("why_here", "tags", "topic", "scope", "utility")}
        topics = [t.strip() for t in (w["row"].get("topic") or "").split(";") if t.strip()]
        row.update({"regulator_key": feeds.get(r["regulator"]), "topics": topics, "large_load": True,
                    "grids": w["grids"], "all_grids": w["all"], "why_here": w["why"], "in_motion": bool(moving[r["id"]])})
        if row["sentence_from"] == "docket list" or "docket list" in (row.get("sentence_kind") or ""):
            row["sentence_kind"] = "docket list"
        out.append(row)
    out = rim.order(out)
    counts = {}
    for name in rim.TABLES:
        p = rim.find(name, dirs)
        counts[name] = len(rim.read_events(p)[0]) if p else None
    return {"built_at_utc": now_iso(), "as_of": today.isoformat(), "tables": counts, "topics": TOPICS, "rows": out,
            "not_in_file": {"count": sum(off.values()), "by_reason": dict(sorted(off.items()))}, "notes": notes}


def refresh_file(last_run):
    if not os.path.exists(FEEDS):
        return None
    with open(FEEDS, encoding="utf-8") as f:
        obj = json.load(f)
    run = None
    if last_run and os.path.exists(last_run):
        with open(last_run, encoding="utf-8") as f:
            run = json.load(f)
    for r in obj["regulators"]:
        mine = (run or {}).get("regulators", {}).get(r["key"])
        r["last_run"] = dict(at_utc=run["at_utc"], **mine) if mine else r.get("last_run")
    return dict({"built_at_utc": now_iso()}, **obj)


def main(argv=None):
    ap = argparse.ArgumentParser(description="ERW: the policy monitor's site files")
    ap.add_argument("--in-dir", action="append", default=[], help="a directory of tables; the first that holds a table wins")
    ap.add_argument("--out-dir", help="a trial: the files under this directory instead of site/data/policy")
    ap.add_argument("--today", help="YYYY-MM-DD (default: today, UTC)")
    ap.add_argument("--last-run", help="policy_monitor_refresh_last_run.json of the refresh step")
    ap.add_argument("--cases", help="also write the tag cases (the fixture both rules are held to) to this file")
    ap.add_argument("--cases-full", help="also write every action held as a case to this file (not for git)")
    ap.add_argument("--only", help="comma separated: tag_rules, action_tags, grids, state_rules, refresh")
    ap.add_argument("--daily", action="store_true", help="the daily run's soft step (see the module's note)")
    args = ap.parse_args(argv)
    dirs = [os.path.abspath(d) for d in args.in_dir]
    out_dir = os.path.abspath(args.out_dir) if args.out_dir else SITE_DIR
    today = dt.date.fromisoformat(args.today) if args.today else dt.datetime.now(dt.timezone.utc).date()
    if args.daily:
        return daily(out_dir, today, dirs or None, args.last_run)
    only = set(args.only.split(",")) if args.only else {"tag_rules", "action_tags", "grids", "state_rules", "refresh"}
    rules = pat.load_rules(RULES)
    done = []
    if "tag_rules" in only:
        copy_rules(out_dir)
        done.append(f"tag_rules.json (version {rules['version']})")
    if "grids" in only:
        write_whole(os.path.join(out_dir, "grids.json"), grids_file())
        done.append("grids.json")
    if "action_tags" in only:
        obj, rows = action_tags(dirs, rules)
        if obj is None:
            done.append("action_tags.json NOT written: policy_actions is not held")
        else:
            write_whole(os.path.join(out_dir, "action_tags.json"), obj)
            done.append(f"action_tags.json ({obj['actions_tagged']} of {obj['actions_read']} actions tagged: "
                        + ", ".join(f"{k} {v}" for k, v in obj["counts"].items()) + ")")
            if args.cases or args.cases_full:
                keep, full = cases(rows, rules)
                for path, part in ((args.cases, keep), (args.cases_full, full)):
                    if path:
                        write_whole(os.path.abspath(path), {"rule_version": str(rules["version"]), "table_rows": len(rows),
                                                            "cases": part})
                        done.append(f"{os.path.basename(path)} ({len(part)} cases)")
    if "state_rules" in only:
        obj = state_rules(dirs, today)
        write_whole(os.path.join(out_dir, "state_rules.json"), obj)
        done.append(f"state_rules.json ({len(obj['rows'])} rows; tables {obj['tables']}; kept out {obj['not_in_file']['count']})")
    if "refresh" in only:
        obj = refresh_file(args.last_run)
        if obj is None:
            done.append("refresh.json NOT written: warehouse/config/policy_monitor_feeds.json is not there")
        else:
            write_whole(os.path.join(out_dir, "refresh.json"), obj)
            done.append(f"refresh.json ({len(obj['regulators'])} regulators, "
                        f"{sum(1 for r in obj['regulators'] if r['refreshed'])} refreshed)")
    for d in done:
        print("policy_monitor_site:", d)
    return 0


if __name__ == "__main__":
    sys.exit(main())
