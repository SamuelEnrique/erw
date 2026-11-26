"""Session 10216: every unit outside Alaska over 200 miles from its EIA county's internal point (finding 6)."""
import glob
import json
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "tests")))
os.environ.setdefault("ERW_GAZETTEER_DIR", sys.argv[1])
import test_audit_map_6 as t  # noqa: E402

d = t.gazetteer_dir()
import zipfile  # noqa: E402
points = {}
for z in sorted(glob.glob(os.path.join(d, "*Gaz_counties*.zip")), key=lambda p: "2020" in p):
    with zipfile.ZipFile(z) as zf:
        for member in zf.namelist():
            raw = zf.read(member)
            text = raw.decode("utf-8-sig") if raw[:3] == b"\xef\xbb\xbf" or b"\xc3" in raw[:200000] else raw.decode("latin-1")
            rows = text.splitlines()
            sep = "|" if "|" in rows[0] else "\t"
            head = [h.strip() for h in rows[0].split(sep)]
            if "USPS" not in head:
                continue
            for ln in rows[1:]:
                v = dict(zip(head, [x.strip() for x in ln.split(sep)]))
                points.setdefault((v["USPS"], t.key(v["NAME"])), (float(v["INTPTLAT"]), float(v["INTPTLONG"])))
f = json.load(open(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "site", "data", "map.json"), encoding="utf-8"))
for i in range(f["kinds"][2]["start"]):
    st = f["states"][f["s"][i]]
    if st == "AK" or f["la"][i] is None or f["c"][i] < 0:
        continue
    hit = points.get((st, t.key(f["counties"][f["c"][i]])))
    if hit:
        m = t.miles(f["la"][i], f["lo"][i], *hit)
        if m > 200:
            print(round(m), st, f["counties"][f["c"][i]], f["names"][f["n"][i]], f["id"][i], f["mw"][i], f["kinds"][f["k"][i]]["slug"], f["la"][i], f["lo"][i])
