#!/usr/bin/env python3
"""Session 1006 (chain 070): the Python package against the conformance file (conformance.json).

Energy Research Warehouse (ERW), docs/methods/packages.md. Each of the twenty calls is made with the Python package
(the fetches, the refusal and the standard on the live set; the citations, licenses and table list from the record)
and its answer compared with the file's. Writes results_python.json and prints one line a call.

    python packages/conformance/run_python.py      exit 0 when every call passes
"""

import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parents[1] / "package" / "src"))

import erw  # noqa: E402


def stamp(t):
    return t.strftime("%Y-%m-%dT%H:%M:%SZ")


def answer(c, live):
    a = c["args"]
    if c["call"] == "fetch":
        erw.set_backend(live)
        df = erw.fetch(a["table"], **{k: v for k, v in a.items() if k != "table"})
        t = df["event_date"] if "event_date" in df else (df["ts_utc"] if "ts_utc" in df else df["status_date"])
        return {"rows": len(df), "first": stamp(t.min()) if len(df) else "", "last": stamp(t.max()) if len(df) else ""}
    if c["call"] == "cite":
        erw.set_backend()
        return {"before_clause": erw.cite(a["table"]).split(", ERW commit")[0].split(", local files")[0] + ","}
    if c["call"] == "license":
        lic = erw.license(a["table"])
        return {"verdict": lic["verdict"], "words": lic["words"]}
    if c["call"] == "refusal":
        erw.set_backend(live)
        try:
            erw.fetch(a["table"], start="2026-10-20")
            return {"message": ""}
        except erw.ERWLicenseHeld as e:
            return {"message": str(e)}
    if c["call"] == "standard":
        erw.set_backend(live)
        s = erw.standard(a["table"])
        return {"shape": s["shape"], "key": s["key"]}
    if c["call"] == "tables":
        erw.set_backend()
        t = erw.tables(backend="local")
        return {"tables": len(t), "public": int((t["verdict"] == "public").sum())}
    raise ValueError(c["call"])


def main() -> int:
    rec = json.loads((HERE / "conformance.json").read_text(encoding="utf-8"))
    erw.requests(reset=True)
    live = erw.LiveBackend()
    results, passed = [], 0
    for c in rec["calls"]:
        try:
            got = answer(c, live)
            ok = got == c["expect"]
        except Exception as e:  # noqa: BLE001 - a call that fails is a call that does not pass, with its error kept
            got, ok = {"error": f"{type(e).__name__}: {e}"}, False
        passed += ok
        results.append({"n": c["n"], "call": c["call"], "pass": ok, "got": got})
        print(f"{'ok  ' if ok else 'FAIL'} {c['n']:02d} {c['call']} {c['args'].get('table', '')}"
              + ("" if ok else f"  got {json.dumps(got)[:160]}"))
    out = {"package": "python", "passed": passed, "of": len(rec["calls"]), "results": results,
           "requests": erw.requests()}
    (HERE / "results_python.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8", newline="\n")
    print(f"{passed} of {len(rec['calls'])} pass; requests {erw.requests()}")
    return 0 if passed == len(rec["calls"]) else 1


if __name__ == "__main__":
    sys.exit(main())
