#!/usr/bin/env python3
"""How stable is the company landscape? Several runs of one niche, compared (session 135).

    python warehouse/thesis/eval/stability.py <state.json> <state.json> [...]

Reads the saved states of warehouse/thesis/run.py (warehouse/output/thesis_state/, internal, not in git) and
compares, by normalized company name (build.name_key): the organisations each run found, and the companies each run
put on the landscape. Prints, for both sets: each run's count, the companies in every run (the core), the union, the
mean pairwise Jaccard overlap (the share of two runs' companies that both hold: 1.0 is identical, 0.0 is disjoint),
and a table of every company with the runs that hold it. No model call; nothing is written.

Session 142: also the pipeline map as a third level, each run's landscape in its own order, and, for states written
since the tie of a company to a trend became a rule (warehouse/thesis/tie.py), every change of a company's place from
one run to the next with the evidence lines (tier, address, hash of the sentence) or the facts that explain it. A
change with no such line is printed as NOT EXPLAINED.
"""
import itertools
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))


def _load(name, path):
    """A neighbouring module by its path, under a name of its own: "build" and "run" are names other folders use too."""
    import importlib.util
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


tb = _load("erw_thesis_build", os.path.join(HERE, "..", "build.py"))

ON_MAP = ("trend", "pipeline")


def sets_of(state):
    found, on_map, names = set(), set(), {}
    for o in state["funnel"]:
        k = tb.name_key(o["name"])
        if not k:
            continue
        names.setdefault(k, o["name"])
        found.add(k)
        if o["reached"] in ON_MAP:
            on_map.add(k)
    return found, on_map, names


def pipeline_of(state):
    return {tb.name_key(o["name"]) for o in state["funnel"] if o["reached"] == "pipeline" and tb.name_key(o["name"])}


def explain(states):
    """Every change of place between consecutive runs, from each run's own record (state["tie"]["diff"])."""
    lines = []
    for n, s in enumerate(states[1:], 2):
        d = (s.get("tie") or {}).get("diff")
        if not d:
            lines.append(f"run {n}: this state carries no record of what changed (written before session 142)")
            continue
        for c in d["new_companies"]:
            lines.append(f"run {n}: NEW {c['name']} (reached: {c['reached']}): first named in this run; its evidence: " +
                         ("; ".join(f"{t} {a}" for t, a, _ in c["evidence"][:4]) or "none that names it"))
        for c in d["gone_companies"]:
            lines.append(f"run {n}: GONE {c['name']} (was: {c['reached']})")
        for m in d["moved"]:
            why = [f"added {t} {a} [{h}]" for t, a, h in m["added"]] + [f"removed {t} {a} [{h}]" for t, a, h in m["removed"]]
            for f, v in m["facts"].items():
                sb = (m.get("fact_sources") or {}).get(f)
                why.append(f"{f}: {v[0]!r} -> {v[1]!r}" + (f" (first stated in run {sb['run_id']}; its row cites {len(sb['sources'])} sources, {len(sb.get('new_sources') or [])} first fetched in that run"
                                                           + (": " + ", ".join(sb["new_sources"][:2]) if sb.get("new_sources") else "") + ")" if sb else ""))
            if m.get("reading_only"):
                why.append("NOT A SOURCE CHANGE: the fact was read by the model from sources the store already held")
            if m.get("by_order"):
                why.append("its own evidence is unchanged: another company's evidence changed and the pipeline map holds a fixed number")
            lines.append(f"run {n}: MOVED {m['name']}: {m['from']} -> {m['to']}, trends {m['trends_from']} -> {m['trends_to']}: " +
                         ("; ".join(why) if m["explained"] else "NOT EXPLAINED"))
    return lines


def jaccard(a, b):
    return len(a & b) / len(a | b) if (a | b) else 1.0


def compare(sets):
    pairs = list(itertools.combinations(range(len(sets)), 2))
    core = set.intersection(*sets) if sets else set()
    union = set.union(*sets) if sets else set()
    return dict(counts=[len(s) for s in sets], core=len(core), union=len(union),
                jaccard=[round(jaccard(sets[i], sets[j]), 3) for i, j in pairs],
                mean_jaccard=round(sum(jaccard(sets[i], sets[j]) for i, j in pairs) / len(pairs), 3) if pairs else 1.0,
                core_names=core, union_names=union)


def main(argv=None):
    paths = (argv if argv is not None else sys.argv[1:])
    if len(paths) < 2:
        print(__doc__)
        return 2
    states = [json.load(open(p, encoding="utf-8")) for p in paths]
    found, on_map, names = [], [], {}
    for s in states:
        f, m, n = sets_of(s)
        found.append(f); on_map.append(m)
        for k, v in n.items():
            names.setdefault(k, v)
    print(f"niche: {states[0]['niche'][:90]}")
    pipe = [pipeline_of(s) for s in states]
    for label, sets in (("organisations found", found), ("companies on the landscape", on_map), ("companies on the pipeline map", pipe)):
        c = compare(sets)
        print(f"\n{label}: per run {c['counts']}; in every run {c['core']}; in any run {c['union']}; "
              f"pairwise Jaccard {c['jaccard']}, mean {c['mean_jaccard']}")
    c = compare(on_map)
    print("\ncompany | " + " | ".join(f"run {i + 1}" for i in range(len(states))) + " | found in")
    for k in sorted(set.union(*found), key=lambda k: (-sum(k in m for m in on_map), -sum(k in f for f in found), k)):
        marks = ["map" if k in m else ("found" if k in f else "-") for f, m in zip(found, on_map)]
        print(f"{names[k]} | " + " | ".join(marks) + f" | {sum(k in f for f in found)} of {len(states)}")
    for i, s in enumerate(states, 1):
        print(f"\nrun {i} ({s['run_id']}), the landscape in its order: " + "; ".join(o["name"] + (" (pipeline)" if o["reached"] == "pipeline" else "") for o in s["funnel"] if o["reached"] in ON_MAP))
    if any(s.get("tie") for s in states):
        print("\nwhat changed from one run to the next, and why:")
        for line in explain(states) or ["nothing: every run holds the same companies at the same place"]:
            print("  " + line)
    return 0


if __name__ == "__main__":
    sys.exit(main())
