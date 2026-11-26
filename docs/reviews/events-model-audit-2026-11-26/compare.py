"""Session 10225: the restated figures (restate.json) against the figures the site's own code draws (the pages drawn to
HTML by site/scripts/events-pages.mjs). A figure agrees when the restated value, rounded to the decimals the page
shows, gives the page's shown number, and the raw values agree to 1e-9 relative. Every figure the three pages and the
three index cards draw is listed; the pair table and net imports are out of bounds (the paper's) and not compared.

    python compare.py <restate.json> <drawn dir> <out.json>
"""
import html
import json
import os
import re
import sys

PAGES = {"uri-2021": "uri_2021", "caiso-heat-2020": "caiso_heat_2020", "elliott-2022": "elliott_2022"}
OUT_OF_BOUNDS = re.compile(r"^wc\|(pair\||[A-Z]+\|imports)")


def drawn(path):
    h = open(path, encoding="utf-8").read()
    out = {}
    for m in re.finditer(r'<span data-check="([^"]+)" data-raw="([^"]*)"[^>]*>([\s\S]*?)</span>', h):
        out[html.unescape(m.group(1))] = (float(m.group(2)), html.unescape(re.sub(r"<[^>]+>", "", m.group(3))))
    for m in re.finditer(r'<span data-n="([^"]+)">([^<]*)</span>', h):
        out[html.unescape(m.group(1))] = (None, html.unescape(m.group(2)))
    return out


def num(s):
    t = s.replace(",", "").replace("+", "").strip()
    try:
        return float(t), (len(t.split(".")[1]) if "." in t else 0)
    except ValueError:
        return None, 0


def main():
    res = json.load(open(sys.argv[1], encoding="utf-8"))["figures"]
    d = sys.argv[2]
    report = {"pages": {}, "summary": {}}
    for slug, ev in list(PAGES.items()) + [("index", None)]:
        got = drawn(os.path.join(d, slug + ".html"))
        if slug == "index":
            got = {k: v for k, v in got.items() if any(e in k for e in PAGES.values())}
        rows, agree, differ, missing, extra, oob = [], 0, 0, 0, 0, 0
        for k, (raw, shown) in sorted(got.items()):
            if OUT_OF_BOUNDS.search(k):
                oob += 1
                continue
            rk = f"{ev}#{k}" if (ev and k.startswith("wc|")) else k
            if rk not in res:
                extra += 1
                rows.append(dict(key=k, shown=shown, restated=None, verdict="drawn, not restated"))
                continue
            v = res[rk]
            n, dec = num(shown)
            ok_shown = n is not None and abs(round(abs(v), dec) - abs(n)) < 10 ** (-dec) / 2 + 1e-9 and (n == 0 or (v < 0) == shown.strip().startswith("-"))
            ok_raw = raw is None or abs(raw - v) <= 1e-9 * max(1.0, abs(v))
            ok = ok_shown and ok_raw
            agree += ok
            differ += not ok
            rows.append(dict(key=k, shown=shown, raw=raw, restated=v, verdict="agrees" if ok else "DIFFERS"))
        keys_here = [k for k in res if (ev and (f"|{ev}" in k or k.startswith(f"es|{ev}|"))) and k not in got and not k.startswith(("wc|", "reached|"))]
        keys_here += [k for k in res if ev and k.startswith(f"{ev}#") and k.split("#", 1)[1] not in got]
        if slug != "index":
            for k in keys_here:
                missing += 1
                rows.append(dict(key=k, restated=res[k], verdict="restated, not drawn"))
        report["pages"][slug] = rows
        report["summary"][slug] = dict(agree=agree, differ=differ, drawn_not_restated=extra, restated_not_drawn=missing, out_of_bounds=oob)
    json.dump(report, open(sys.argv[3], "w", encoding="utf-8"), indent=1)
    print(json.dumps(report["summary"], indent=1))
    for slug, rows in report["pages"].items():
        for r in rows:
            if r["verdict"] != "agrees":
                print(slug, r)


if __name__ == "__main__":
    main()
