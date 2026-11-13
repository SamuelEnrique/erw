#!/usr/bin/env python3
"""Sessions 5202 and 5251 (chains 235 and 238): a set of questions asked through the site's own loop with no build and no
server, graded on the set's keys, under a spend cap.

Energy Research Warehouse (ERW). eval_loop.py asks through the Python loop, which lists the package's tables under the
key the machine holds; a visitor's chat is the site's loop (site/lib/chat/ask.ts ask(), the function /api/ask calls),
which reads the catalogue and the rows a visitor's key reads. This runner asks through that one:

    python warehouse/chat/eval/eval_site.py --session 5251 --set platform --cap 2 [--slice a|b] [--only pw01,pw02] [--first 20]
                                            [--no-ask] [--rules 5251|5201|2223|none] [--no-ledger] [--dry-run]

  questions  the set's YAML (eval_s1113.py SETS) as {"questions": [{id, grid, via, question}]}, written to
             runs/ask_eval/<set>_questions.json (runs/ is not in git); a key is never sent to the asking
  ask        site/scripts/eval-ask-site-loop.mjs under Node (the loader of site/scripts/eval-loader.mjs: a worktree with no
             node_modules reads the main checkout's), every read with the anon key, every tool call recorded.
             A session's asking is its own run file, eval_s<N>_site_<set>_run.json (a question's record is about 60 KB:
             the catalogue it listed is in it), written after every question and read first, so an asking goes on where
             it stopped. A question in any earlier session's run of the set is not asked again unless named with --only.
             --cap is THIS session's ceiling in USD (USD 2 a session). --first N asks at most the next N.
             --slice a or b asks one half of the set (slices): a question through the site's loop cost USD 0.04 to 0.23 on
             13 November 2026 (USD 0.14 on average), so 134 are about USD 18 and a chain's USD 20 buys the set once; half
             is asked first, the classes of failure it shows are fixed, and the other half, never asked before, is the
             held-out measure
  grade      every run of the set graded again by eval_s1113.py's grade_set under eval_s267.py's RULES_5251 (the rules of
             sessions 2223 and 5201, and hold_public_grids: a held grid's question answered with the public grids'
             figures, as the loop is built to), or under --rules, each into its eval_s<N>_site_<set>_grades.json with the
             counts by kind and by sector; then the counts over all of them, a question's newest answer standing
  record     a run not yet in runs.json (the one list of the stored runs) is named there, and the records written
             from the stored runs are written again: docs/reviews/ask-history.md, ask-replay.md and ask-refusals.md
             (history.py, replay.py, refusals.py) and, for the platform set, the scores of its review file
             (platform_scores.py); each exit code is printed and the first that is not 0 is returned

Each model call is one row of the site's cost ledger (site_api_calls, the step site_ask_eval, which no public ceiling
counts: migration 035), written with the service key as the server writes it; --no-ledger leaves the key out, and the
cost then stands in the run file alone. Nothing of the warehouse is written.
"""
import glob
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
SITE = os.path.join(ROOT, "site")
KINDS = ("figure", "hold", "pause", "not_live", "outside", "gap", "partial")


def module(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def files(session, which, here=HERE):
    tag = f"eval_s{session}_site_{which}"
    return {k: os.path.join(here, f"{tag}_{k}.json") for k in ("run", "grades")}


def sessions_of(which, here=HERE):
    """The sessions that hold a run of the set, oldest first (by number)."""
    found = []
    for p in glob.glob(os.path.join(here, f"eval_s*_site_{which}_run.json")):
        m = re.fullmatch(rf"eval_s(\d+)_site_{re.escape(which)}_run\.json", os.path.basename(p))
        if m:
            found.append(m.group(1))
    return sorted(found, key=int)


def read_json(path):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def write_json(path, doc):
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        json.dump(doc, f, indent=1, ensure_ascii=False)
        f.write("\n")


def spent(run_path):
    """(the cost of a run so far in USD, the questions it holds)."""
    if not os.path.exists(run_path):
        return 0.0, 0
    qs = read_json(run_path).get("questions") or []
    return round(sum(float(x.get("cost_usd") or 0) for x in qs), 6), len(qs)


def asked_ids(which, here=HERE):
    """The ids in any run of the set."""
    ids = set()
    for s in sessions_of(which, here):
        ids |= {x["id"] for x in (read_json(files(s, which, here)["run"]).get("questions") or [])}
    return ids


def asking(qs, done_ids, only=None, first=None):
    """The ids this asking takes, in the set's order: the named ones, or those not yet in a run, at most `first`."""
    ids = [q["id"] for q in qs if (q["id"] in only if only else q["id"] not in done_ids)]
    return ids[:first] if first else ids


def slices(qs):
    """Session 5251: the set in two halves that each cover every area and every kind. A question whose number is odd
    (pw01, pw03, ...) is in slice a and one whose number is even in slice b, so a question's half does not move when
    another's key changes; the kinds gap and partial (the days and the months the live set holds in part, which a later
    load may fill) go whole to slice a. Returns (a's ids, b's ids)."""
    a, b = [], []
    for q in qs:
        m = re.search(r"(\d+)$", q["id"])
        odd = bool(m) and int(m.group(1)) % 2 == 1
        (a if odd or q.get("kind") in ("gap", "partial") else b).append(q["id"])
    return a, b


def node_command(questions_path, run_path, cap_total, ids, label, ledger=True, dry_run=False):
    """The runner's command, run from site/. `ids` are the questions it asks (it asks a named one whether or not this
    session's run holds it, so the caller names only what is due)."""
    cmd = ["node", "--import", "./scripts/eval-register.mjs", "scripts/eval-ask-site-loop.mjs", "--questions", questions_path, "--run", run_path,
           "--cap", f"{cap_total:.4f}", "--label", label, "--only", ",".join(ids)]
    if not ledger:
        cmd.append("--no-ledger")
    if dry_run:
        cmd.append("--dry-run")
    return cmd


def counts(rows, qs):
    """Right and asked by kind and by sector, for a set that carries them (questions_platform.yaml)."""
    by = {q["id"]: q for q in qs}
    out = {"by_kind": {}, "by_sector": {}}
    for r in rows:
        q = by.get(r["id"]) or {}
        for field, key in (("by_kind", "kind"), ("by_sector", "sector")):
            v = q.get(key)
            if v:
                c = out[field].setdefault(v, {"asked": 0, "right": 0})
                c["asked"] += 1
                c["right"] += 1 if r["ok"] else 0
    return {k: v for k, v in out.items() if v}


def entry(session, which, questions_file):
    """A run's entry of runs.json, in the form the list keeps."""
    tag = f"eval_s{session}_site_{which}"
    return {"file": f"{tag}_run.json", "grades": f"{tag}_grades.json", "right": "ok",
            "label": f"session {session}, the site's loop, the {which} set", "limit": 12, "replay": True,
            "history": {"kind": "right", "set": f"`{questions_file}`",
                        "what": (f"questions of the {which} set asked in session {session} through the site's own loop with no build and a visitor's key "
                                 "(`eval_site.py`); the count is of this session's asking"),
                        "where": f"`docs/reviews/ask-eval-2026-11-13.md`; session {session}'s report"}}


def register(session, which, questions_file, path=None):
    """Names the session's run in runs.json when it is not there yet (after the last run, the file's own indent kept).
    Returns True when the list was changed."""
    path = path or os.path.join(HERE, "runs.json")
    with open(path, encoding="utf-8") as f:
        text = f.read()
    e = entry(session, which, questions_file)
    if any(r["file"] == e["file"] for r in json.loads(text)["runs"]):
        return False
    at = text.index('\n ],\n "left_out"')
    block = "\n".join("  " + line for line in json.dumps(e, indent=1, ensure_ascii=False).split("\n"))
    text = text[:at] + ",\n" + block + text[at:]
    json.loads(text)
    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write(text)
    return True


def records(which=None):
    """history.py, replay.py and refusals.py written again from the stored runs (and the platform set's scores in its
    review file, session 5252); the first exit code that is not 0."""
    worst = 0
    for name in ("history.py", "replay.py", "refusals.py") + (("platform_scores.py",) if which == "platform" else ()):
        code = subprocess.run([sys.executable, os.path.join(HERE, name)], stdin=subprocess.DEVNULL, stdout=subprocess.DEVNULL).returncode
        print(f"{name}: exit {code}")
        worst = worst or code
    return worst


def grade_all(E, which, qs, rules, here=HERE):
    """Every run of the set graded again under `rules`, each into its grades file. Returns the rows over all of them, one
    a question, the newest session's answer standing, each with the session it was asked in."""
    newest = {}
    keep = dict(E.SETS[which])
    try:
        for s in sessions_of(which, here):
            F = files(s, which, here)
            E.SETS[which]["run"], E.SETS[which]["grades"] = F["run"], F["grades"]
            doc = E.grade_set(which, rules)
            doc["loop"] = "site"
            doc.update(counts(doc["questions"], qs))
            write_json(F["grades"], doc)
            for r in doc["questions"]:
                newest[r["id"]] = {**r, "session": s}
    finally:
        E.SETS[which].update(keep)
    return [newest[q["id"]] for q in qs if q["id"] in newest]


def main(argv):
    def val(name, default=None):
        return argv[argv.index(name) + 1] if name in argv else default
    if "--session" not in argv:
        raise SystemExit("--session <N> is required (the files are named by it)")
    session, which = val("--session"), val("--set", "platform")
    cap = float(val("--cap", "2"))
    only = [x for x in val("--only", "").split(",") if x] or None
    first = int(val("--first")) if "--first" in argv else None
    E = module("eval_s1113_for_site", os.path.join(HERE, "eval_s1113.py"))
    if which not in E.SETS or not E.SETS[which]["questions"]:
        raise SystemExit(f"--set must be a set with a questions file, one of {sorted(k for k, v in E.SETS.items() if v['questions'])}")
    F = files(session, which)
    qs = E.questions(E.SETS[which]["questions"])
    if "--no-ask" not in argv:
        if not shutil.which("node"):
            raise SystemExit("node is not on the PATH: the site's loop cannot be run")
        qdir = os.path.join(ROOT, "runs", "ask_eval")
        os.makedirs(qdir, exist_ok=True)
        qpath = os.path.join(qdir, f"{which}_questions.json")
        write_json(qpath, {"questions": [{k: q.get(k) for k in ("id", "grid", "via", "question")} for q in qs]})
        before, n_before = spent(F["run"])
        done = asked_ids(which)
        which_slice = val("--slice")
        if which_slice:
            if which_slice not in ("a", "b") or only:
                raise SystemExit("--slice is a or b, and goes without --only")
            part = set(slices(qs)[0 if which_slice == "a" else 1])
            ids = [q["id"] for q in qs if q["id"] in part and q["id"] not in done][: first or None]
        else:
            ids = asking(qs, done, only, first)
        print(f"asking {len(ids)} of {len(qs)} ({len(done)} in the set's runs so far; this session's run holds {n_before}, USD {before:.4f}); this session's cap USD {cap:.2f}")
        label = (f"Session {session} ({which}): questions of {os.path.basename(E.SETS[which]['questions'])} asked through the site's own loop "
                 "(site/lib/chat/ask.ts ask(), no build, every read with the anon key), every tool call recorded, by eval_site.py and "
                 "site/scripts/eval-ask-site-loop.mjs under the ledger step site_ask_eval.")
        code = 0
        if ids or "--dry-run" in argv:
            cmd = node_command(qpath, F["run"], cap, ids or [qs[0]["id"]], label, ledger="--no-ledger" not in argv, dry_run="--dry-run" in argv)
            code = subprocess.run(cmd, cwd=SITE, stdin=subprocess.DEVNULL).returncode
        else:
            print("nothing left to ask of what was named")
        after, n_after = spent(F["run"])
        print(f"this asking: {n_after - n_before} questions, USD {after - before:.4f}; this session's run: {n_after} questions, USD {after:.4f} of the cap USD {cap:.2f}")
        if code != 0:
            print(f"eval_site: the runner ended with exit {code}", file=sys.stderr)
            return code
        if "--dry-run" in argv:
            return 0
    if not sessions_of(which):
        raise SystemExit(f"no run of the set {which} to grade")
    how = val("--rules", "5251")
    rules = {"none": (), "2223": E.G.RULES_2223, "5201": E.G.RULES_5201, "5251": E.G.RULES_5251}.get(how)
    if rules is None:
        raise SystemExit("--rules is one of 5251, 5201, 2223, none")
    rows = grade_all(E, which, qs, rules)
    total = sum(float(spent(files(s, which)["run"])[0]) for s in sessions_of(which))
    print(f"the set over its runs ({', '.join(sessions_of(which))}): right {sum(1 for r in rows if r['ok'])} of {len(rows)} asked, of {len(qs)}; USD {total:.4f}")
    c = counts(rows, qs)
    for field in ("by_kind", "by_sector"):
        if field in c:
            print(field + ": " + ", ".join(f"{k} {v['right']} of {v['asked']}" for k, v in c[field].items()))
    wrong = [r["id"] for r in rows if not r["ok"]]
    print("not right: " + (", ".join(wrong) if wrong else "none"))
    if os.path.exists(F["run"]) and register(session, which, os.path.basename(E.SETS[which]["questions"])):
        print(f"runs.json: {os.path.basename(F['run'])} named")
    return records(which)


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
