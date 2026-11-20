"""Energy Research Warehouse (ERW), session 8901 (chain 507, part C): the four problem sets of the whole country, recomputed.

Run from the repository's root:

    python replication/problem_sets/replicate_country.py [--compare figures.json]

It reads the committed page files the sets read (site/data/regions/trade/ten.json, site/data/regions/trade_matrix.json,
site/data/regions/events/elliott_2022.json and uri_2021.json, site/data/resources/manifest.json, site/data/industry.json)
with Python's json module alone, none of the site's code, and recomputes every figure of every answer by the sets' rules
(the month, the years, the peak hour, the layer and the industries are found again here). It writes:

    replication/problem_sets/country_inputs.csv    every figure read from a file, as the JSON gives it (pos: a position of an
                                                   hourly series, for the peak hours), with its file and path
    replication/problem_sets/country_answers.csv   every figure of every question: read (equal to an input), calc (op of two
                                                   figures) or max (the largest of a series), with its value

replicate_country.do recomputes the calc and max rows from the inputs in Stata. With --compare, it reads the figures the
site's own code builds (site/scripts/problem-sets-country-figures.mjs) and checks that every figure of every answer the
site shows is one recomputed here, and every figure recomputed here is one the site shows in that question, each to a
relative 1e-9. Exit 0 when all hold, 1 otherwise. No network, no model; no number typed.
"""
from __future__ import annotations

import csv
import json
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA = os.path.join(ROOT, "site", "data")
OUT = os.path.join(ROOT, "replication", "problem_sets")


def load(rel):
    with open(os.path.join(DATA, *rel.split("/")), encoding="utf-8") as f:
        return json.load(f)


class Sheet:
    """The inputs and the figures of every question."""

    def __init__(self):
        self.inputs, self.answers = [], []
        self.seen_inputs = set()

    def read(self, s, q, name, file, path, value):
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            raise ValueError(f"{s} {q} {name}: no number at {file} {path}")
        self._input(s, q, name, "", value, file, path)
        self.answers.append({"set": s, "question": q, "figure": name, "kind": "read", "op": "", "a": "", "b": "", "value": value})
        return value

    def series(self, s, q, name, file, path, values):
        for i, v in enumerate(values):
            if isinstance(v, (int, float)) and not isinstance(v, bool):
                self._input(s, q, name, str(i), v, file, f"{path}/{i}")

    def peak(self, s, q, name, series_name, values):
        best = max((i for i, v in enumerate(values) if isinstance(v, (int, float))), key=lambda i: (values[i], -i))
        self.answers.append({"set": s, "question": q, "figure": name, "kind": "max", "op": "", "a": series_name, "b": "", "value": values[best]})
        return best

    def calc(self, s, q, name, op, a, b):
        x, y = self.value(s, q, a), self.value(s, q, b)
        v = x / y if op == "ratio" else x - y if op == "diff" else x / y * 100
        self.answers.append({"set": s, "question": q, "figure": name, "kind": "calc", "op": op, "a": a, "b": b, "value": v})
        return v

    def value(self, s, q, name):
        for r in self.answers:
            if r["set"] == s and r["question"] == q and r["figure"] == name:
                return r["value"]
        raise KeyError(f"{s} {q} {name}")

    def _input(self, s, q, name, pos, value, file, path):
        key = (s, q, name, pos)
        if key in self.seen_inputs:
            return
        self.seen_inputs.add(key)
        self.inputs.append({"set": s, "question": q, "name": name, "pos": pos, "value": value, "file": f"site/data/{file}", "path": path})


def trade(sh):
    S, T, M = "who-trades-with-whom", "regions/trade/ten.json", "regions/trade_matrix.json"
    t, m = load(T), load(M)
    i = max(j for j, mo in enumerate(t["months"]) if mo < t["built"][:7])
    nb = t["neighbors"]

    def own(q, name, c, f="net_imports_mwh", j=None):
        j = i if j is None else j
        return sh.read(S, q, name, T, f"neighbors/{c}/{f}/{j}", nb[c][f][j])

    own("tx", "own", "SE"); own("tx", "their", "SE", "their_report_mwh"); sh.calc(S, "tx", "ratio", "ratio", "own", "their")
    sh.read(S, "t1", "total", T, f"net_imports_mwh/{i}", t["net_imports_mwh"][i])
    for c in sorted(nb):
        own("t1", c, c)
    own("t2", "own", "MIDW"); own("t2", "their", "MIDW", "their_report_mwh"); own("t2", "gap", "MIDW", "gap_mwh"); sh.calc(S, "t2", "ratio", "ratio", "own", "their")
    own("t3", "own", "MIDA"); own("t3", "their", "MIDA", "their_report_mwh"); own("t3", "gap", "MIDA", "gap_mwh"); sh.calc(S, "t3", "diff", "diff", "own", "their")
    for f in ("hours_own", "hours_their", "hours_both"):
        own("t3", f, "MIDA", f)

    def whole(p):
        return p["months_held"] == 12 and p["months_in_year"] == 12 and p["a_report_mwh"] is not None and p["b_report_mwh"] is not None and p["gap_mwh"] is not None

    def row(a, b, y):
        hits = [p for p in m["region_pairs"] if p["a"] == a and p["b"] == b and p["year"] == y]
        assert len(hits) == 1, (a, b, y)
        return hits[0]

    mt = [p for p in m["region_pairs"] if p["a"] == "MIDA" and p["b"] == "TEN" and whole(p)]
    # the year whose gap is largest in size; of equal gaps the first in the file's order
    py = [p["year"] for p in mt if abs(p["gap_mwh"]) == max(abs(x["gap_mwh"]) for x in mt)][0]
    for f, n in (("a_report_mwh", "a"), ("b_report_mwh", "b"), ("gap_mwh", "gap")):
        sh.read(S, "t4", n, M, f"region_pairs/@a=MIDA+b=TEN+year={py}/{f}", row("MIDA", "TEN", py)[f])
    sh.calc(S, "t4", "diff", "diff", "a", "b")
    years = sorted(p["year"] for p in m["region_pairs"] if p["a"] == "MIDW" and p["b"] == "TEN" and whole(p))
    y0, y1 = years[0], years[-1]
    for y in (y0, y1):
        for f, n in (("b_report_mwh", "ten"), ("a_report_mwh", "midw")):
            sh.read(S, "t5", f"{n}{y}", M, f"region_pairs/@a=MIDW+b=TEN+year={y}/{f}", row("MIDW", "TEN", y)[f])
    sh.calc(S, "t5", "ratio_ten", "ratio", f"ten{y1}", f"ten{y0}"); sh.calc(S, "t5", "ratio_midw", "ratio", f"midw{y1}", f"midw{y0}")
    cy = max(p["year"] for p in m["region_pairs"] if p["a"] == "CAL" and p["b"] == "MEX" and p["months_in_year"] == 12)
    for f in ("a_report_mwh", "hours_a", "hours_b"):
        sh.read(S, "t6", f, M, f"region_pairs/@a=CAL+b=MEX+year={cy}/{f}", row("CAL", "MEX", cy)[f])
    hours = nb["MIDW"]["hours_own"]
    shares = [(hours[j] / t["hours_in_month"][j], j) for j in range(len(hours)) if isinstance(hours[j], (int, float)) and t["months"][j] < t["built"][:7]]
    k = min(shares)[1]   # the smallest share; of equal shares the earliest month
    sh.read(S, "t7", "hours", T, f"neighbors/MIDW/hours_own/{k}", hours[k]); sh.read(S, "t7", "in_month", T, f"hours_in_month/{k}", t["hours_in_month"][k])
    own("t7", "own", "MIDW", j=k); sh.calc(S, "t7", "pct", "pct", "hours", "in_month")


def storm(sh):
    S, E, U = "storm-across-the-country", "regions/events/elliott_2022.json", "regions/events/uri_2021.json"
    el, ur = load(E), load(U)

    def peak(q, file, f, r, tag=""):
        d = f["regions"][r]["demand_mw"]
        sh.series(S, q, f"{tag}demand_series", file, f"regions/{r}/demand_mw", d)
        i = sh.peak(S, q, f"{tag}peak_max", f"{tag}demand_series", d)
        sh.read(S, q, f"{tag}demand", file, f"regions/{r}/demand_mw/{i}", d[i])
        sh.read(S, q, f"{tag}baseline", file, f"regions/{r}/baseline/demand_mw/{i}", f["regions"][r]["baseline"]["demand_mw"][i])
        return i

    def at(q, name, file, f, r, path):
        node = f["regions"][r]
        for p in path:
            node = node[p]
        return sh.read(S, q, name, file, f"regions/{r}/" + "/".join(str(p) for p in path), node)

    peak("sx", E, el, "CAR"); sh.calc(S, "sx", "ratio", "ratio", "demand", "baseline")
    tn = peak("s1", E, el, "TEN"); sh.calc(S, "s1", "ratio", "ratio", "demand", "baseline")
    tx = peak("s2", U, ur, "TEX"); sh.calc(S, "s2", "diff", "diff", "demand", "baseline")
    for src in ("natural_gas", "coal", "nuclear", "hydro"):
        at("s3", src, E, el, "TEN", ["gen", src, tn])
    at("s3", "net", E, el, "TEN", ["net_generation_mw", tn]); at("s3", "gas_base", E, el, "TEN", ["baseline", "gen", "natural_gas", tn])
    sh.calc(S, "s3", "pct", "pct", "natural_gas", "net"); sh.calc(S, "s3", "ratio", "ratio", "natural_gas", "gas_base")
    for src in ("wind", "natural_gas"):
        at("s4", src, U, ur, "TEX", ["gen", src, tx]); at("s4", f"{src}_base", U, ur, "TEX", ["baseline", "gen", src, tx])
    sh.calc(S, "s4", "wind_diff", "diff", "wind", "wind_base"); sh.calc(S, "s4", "gas_ratio", "ratio", "natural_gas", "natural_gas_base")
    at("s5", "imports", E, el, "TEN", ["net_imports_mw", tn]); at("s5", "imports_base", E, el, "TEN", ["baseline", "net_imports_mw", tn])
    for k in sorted(p for p in el["pairs"] if p.endswith("-TEN")):
        sh.read(S, "s5", k, E, f"pairs/{k}/flow_mw/{tn}", el["pairs"][k]["flow_mw"][tn])
    at("s6", "tex_imports", U, ur, "TEX", ["net_imports_mw", tx]); at("s6", "ten_imports", E, el, "TEN", ["net_imports_mw", tn])
    at("s6", "tex_demand", U, ur, "TEX", ["demand_mw", tx]); at("s6", "ten_demand", E, el, "TEN", ["demand_mw", tn])
    sh.calc(S, "s6", "ratio", "ratio", "ten_imports", "tex_imports")
    for f in ("flow_mw_a", "flow_mw_b"):
        sh.read(S, "s7", f, U, f"pairs/CENT-TEX/{f}/{tx}", ur["pairs"]["CENT-TEX"][f][tx])
    sh.calc(S, "s7", "diff", "diff", "flow_mw_a", "flow_mw_b")


def ground(sh):
    S, F = "under-the-ground-and-in-the-wind", "resources/manifest.json"
    m = load(F)

    def layer(i):
        hits = [x for x in m["layers"] if x["id"] == i]
        assert len(hits) == 1, i
        return hits[0]

    def at(q, name, i, *path):
        node = layer(i)
        for p in path:
            node = node[p]
        return sh.read(S, q, name, F, f"layers/@id={i}/" + "/".join(path), node)

    at("rx", "min", "solar_ghi", "legend", "min"); at("rx", "max", "solar_ghi", "legend", "max"); sh.calc(S, "rx", "ratio", "ratio", "max", "min")
    at("r1", "legend_max", "wind_speed_100m", "legend", "max"); at("r1", "source_max", "wind_speed_100m", "source_stats", "max")
    sh.calc(S, "r1", "diff", "diff", "source_max", "legend_max")
    at("r2", "ghi", "solar_ghi", "legend", "max"); at("r2", "dni", "solar_dni", "legend", "max"); sh.calc(S, "r2", "ratio", "ratio", "dni", "ghi")
    at("r3", "mean", "wind_capacity_factor", "stats", "mean"); at("r3", "max", "wind_capacity_factor", "stats", "max"); sh.calc(S, "r3", "ratio", "ratio", "max", "mean")
    at("r4", "n", "geothermal_hydrothermal_sites", "stats", "n"); at("r4", "total", "geothermal_hydrothermal_sites", "total_mwe_mean")
    at("r4", "max", "geothermal_hydrothermal_sites", "stats", "max"); sh.calc(S, "r4", "pct", "pct", "max", "total")
    at("r5", "cap", "hydropower_npd", "total_cap_mw"); at("r5", "gen", "hydropower_npd", "total_gen_mwh_yr"); sh.calc(S, "r5", "hours", "ratio", "gen", "cap")
    at("r6", "total", "biomass", "national_total"); at("r6", "crop", "biomass", "parts", "CropRes"); sh.calc(S, "r6", "pct", "pct", "crop", "total")


def where(sh):
    S, F = "where-energy-goes", "industry.json"
    d = load(F)
    mo, ind, sa = d["monthly"], d["industries"], d["states_annual"]
    j = max(k for k, v in enumerate(mo["by_source"]["total"]) if isinstance(v, (int, float)))
    jp = mo["months"].index(f"{int(mo['months'][j][:4]) - 1}{mo['months'][j][4:]}")
    first, second = ind["ranked_3_digit"][0], ind["ranked_3_digit"][1]

    def mf(q, name, src, k):
        return sh.read(S, q, name, F, f"monthly/by_source/{src}/{k}", mo["by_source"][src][k])

    def inf(q, name, code, region, fuel):
        return sh.read(S, q, name, F, f"industries/industries/{code}/by_region/{region}/{fuel}", ind["industries"][code]["by_region"][region][fuel])

    inf("ix", "gas", first, "us", "natural_gas"); inf("ix", "total", first, "us", "total"); sh.calc(S, "ix", "pct", "pct", "gas", "total")
    mf("i1", "total", "total", j); mf("i1", "end", "end_use_total", j); mf("i1", "losses", "electrical_system_losses", j); sh.calc(S, "i1", "diff", "diff", "total", "end")
    mf("i2", "now", "total", j); mf("i2", "before", "total", jp); sh.calc(S, "i2", "ratio", "ratio", "now", "before")
    inf("i3", "first", first, "us", "total"); inf("i3", "second", second, "us", "total"); sh.calc(S, "i3", "ratio", "ratio", "first", "second")
    inf("i4", "other", second, "us", "other"); inf("i4", "total", second, "us", "total"); sh.calc(S, "i4", "pct", "pct", "other", "total")
    for name, part in (("onsite", "elec_onsite_generation"), ("net", "elec_net_demand")):
        sh.read(S, "i5", name, F, f"industries/industries/{first}/electricity_mwh/us/{part}", ind["industries"][first]["electricity_mwh"]["us"][part])
    sh.calc(S, "i5", "pct", "pct", "onsite", "net")
    inf("i6", "south", first, "south", "total"); inf("i6", "us", first, "us", "total"); sh.calc(S, "i6", "pct", "pct", "south", "us")
    tx, la = sa["states"]["TX"]["consumption_tbtu"]["total"], sa["states"]["LA"]["consumption_tbtu"]["total"]
    y = max(k for k in range(len(sa["years"])) if isinstance(tx[k], (int, float)) and isinstance(la[k], (int, float)))
    sh.read(S, "i7", "tx", F, f"states_annual/states/TX/consumption_tbtu/total/{y}", tx[y]); sh.read(S, "i7", "la", F, f"states_annual/states/LA/consumption_tbtu/total/{y}", la[y])
    sh.calc(S, "i7", "ratio", "ratio", "tx", "la")


def authority(sh):
    """Session 8905 (chain 590, part C): the fifth set, the Tennessee Valley Authority's own facts, with ERCOT and CAISO."""
    S, A, E, C = "your-own-balancing-authority", "regions/authority/tva.json", "regions/authority/erco.json", "regions/authority/ciso.json"
    a, e, c = load(A), load(E), load(C)

    def first_max(rows, field):
        return max(range(len(rows)), key=lambda i: (rows[i][field], -i))

    def cap(q, name, g):
        return sh.read(S, q, name, A, f"owns/capacity_mw/{g}", a["owns"]["capacity_mw"][g])

    def total(q):
        return sh.read(S, q, "total", A, "owns/total_mw", a["owns"]["total_mw"])

    cap("bx", "nuclear", "nuclear"); total("bx"); sh.calc(S, "bx", "pct", "pct", "nuclear", "total")
    sh.read(S, "b1", "plant", A, "owns/largest_plants/0/mw", a["owns"]["largest_plants"][0]["mw"]); total("b1"); sh.calc(S, "b1", "pct", "pct", "plant", "total")
    cap("b2", "cap_nuclear", "nuclear"); cap("b2", "cap_gas", "natural_gas"); total("b2")
    sh.calc(S, "b2", "cn", "pct", "cap_nuclear", "total"); sh.calc(S, "b2", "cg", "pct", "cap_gas", "total")
    for name, g in (("gen_nuclear", "nuclear"), ("gen_gas", "natural_gas")):
        sh.read(S, "b2", name, A, f"burns/share_pct/{g}", a["burns"]["share_pct"][g])
    ri = first_max(a["coming"]["retirements"], "mw")
    rr = a["coming"]["retirements"][ri]
    sh.read(S, "b3", "retire", A, f"coming/retirements/{ri}/mw", rr["mw"]); cap("b3", "fleet", rr["technology_group"]); sh.calc(S, "b3", "pct", "pct", "retire", "fleet")
    ai = first_max(a["coming"]["additions"], "mw")
    ar = a["coming"]["additions"][ai]
    sh.read(S, "b4", "add", A, f"coming/additions/{ai}/mw", ar["mw"]); cap("b4", "fleet", ar["technology_group"]); sh.calc(S, "b4", "pct", "pct", "add", "fleet")
    pi = first_max(a["trades"]["partners"], "exchange_gross_mwh")
    p = a["trades"]["partners"][pi]
    sh.read(S, "b5", "net", A, f"trades/partners/{pi}/net_import_mwh", p["net_import_mwh"]); sh.read(S, "b5", "gross", A, f"trades/partners/{pi}/exchange_gross_mwh", p["exchange_gross_mwh"])
    sh.calc(S, "b5", "pct", "pct", "net", "gross"); sh.read(S, "b5", "share", A, "trades/net_import_share_of_demand_pct", a["trades"]["net_import_share_of_demand_pct"])
    sh.read(S, "b6", "ercot", E, "burns/co2/intensity_kg_per_mwh", e["burns"]["co2"]["intensity_kg_per_mwh"]); sh.read(S, "b6", "caiso", C, "burns/co2/intensity_kg_per_mwh", c["burns"]["co2"]["intensity_kg_per_mwh"])
    sh.calc(S, "b6", "ratio", "ratio", "ercot", "caiso")
    sh.read(S, "b7", "peak", A, "size/peak_mw", a["size"]["peak_mw"]); sh.read(S, "b7", "growth_tva", A, "size/growth_since_2019_pct", a["size"]["growth_since_2019_pct"])
    sh.read(S, "b7", "growth_ercot", E, "size/growth_since_2019_pct", e["size"]["growth_since_2019_pct"]); sh.calc(S, "b7", "diff", "diff", "growth_ercot", "growth_tva")
    sh.read(S, "b7", "ll_tva", A, "large_loads/count", a["large_loads"]["count"]); sh.read(S, "b7", "ll_ercot", E, "large_loads/count", e["large_loads"]["count"])


def write(path, rows, cols, head):
    with open(path, "w", encoding="utf-8", newline="") as f:
        f.write(head)
        w = csv.DictWriter(f, fieldnames=cols, lineterminator="\n")
        w.writeheader()
        for r in rows:
            w.writerow({k: (repr(v) if isinstance(v, float) else v) for k, v in r.items()})


def close(a, b):
    return abs(a - b) <= 1e-9 * max(1.0, abs(a), abs(b))


def main(argv):
    sh = Sheet()
    trade(sh); storm(sh); ground(sh); where(sh); authority(sh)  # session 8905: the fifth set
    note = "# Energy Research Warehouse (ERW), session 8901: written by replication/problem_sets/replicate_country.py from the committed page files under site/data (each row names its file and path); no number typed.\n"
    write(os.path.join(OUT, "country_inputs.csv"), sh.inputs, ["set", "question", "name", "pos", "value", "file", "path"], note)
    write(os.path.join(OUT, "country_answers.csv"), sh.answers, ["set", "question", "figure", "kind", "op", "a", "b", "value"], note)
    qs = {(r["set"], r["question"]) for r in sh.answers}
    print(f"{len(qs)} questions and examples, {len(sh.answers)} figures recomputed, {len(sh.inputs)} inputs read")
    if "--compare" not in argv:
        return 0
    with open(argv[argv.index("--compare") + 1], encoding="utf-8") as f:
        site = json.load(f)
    bad = []
    for slug, questions in site.items():
        for qid, figs in questions.items():
            mine = [r["value"] for r in sh.answers if r["set"] == slug and r["question"] == qid]
            if not mine:
                bad.append(f"{slug} {qid}: not recomputed here")
                continue
            for v in figs["answer"]:
                if not any(close(v, x) for x in mine):
                    bad.append(f"{slug} {qid}: the answer's {v} is not recomputed here")
            for x in mine:
                if not any(close(v, x) for v in figs["all"]):
                    bad.append(f"{slug} {qid}: {x}, recomputed here, is not on the page")
    site_qs = {(s, q) for s, v in site.items() for q in v}
    for k in sorted(qs - site_qs):
        bad.append(f"{k[0]} {k[1]}: recomputed here, not on the page")
    n_answer = sum(len(f["answer"]) for v in site.values() for f in v.values())
    print(f"compared: {len(site_qs)} questions, {n_answer} answer figures; {len(bad)} differ")
    for b in bad[:40]:
        print("DIFFER", b)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
