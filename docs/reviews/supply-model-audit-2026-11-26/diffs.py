"""Session 10222: the rows where the restatement and the file differ, side by side."""
import json
import sys

F = {r["id"]: r for r in json.load(open(sys.argv[1], encoding="utf-8"))["rows"]}
R = json.load(open(sys.argv[2], encoding="utf-8"))
print(json.dumps(R["summary"]))
for rid, v in R["rows"].items():
    if not v["file_vs_restated"]:
        continue
    f, x = F[rid], v["restated"]
    print("==", rid, v["file_vs_restated"])
    for k in v["file_vs_restated"]:
        k0 = k.split(".")[0]
        print("   file    ", k0, json.dumps(f.get(k0) if k0 != "last" else f["last"]))
        print("   restated", k0, json.dumps(x.get(k0) if k0 != "last" else {"t": x["t"], "v": x["v"]}, default=str))
