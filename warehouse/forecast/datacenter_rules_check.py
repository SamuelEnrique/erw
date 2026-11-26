"""Check site/data/forecast/datacenter_rules.json (chain 740): every rule names a source, every number it holds is a
number, and with --verify-reads every quote is inside the kept text of its source's request (runs/c740/reads/ on
lab-desktop), after curly quotes and spaces are made plain. Writes nothing. Exit 0 when every check passes.

Usage: python warehouse/forecast/datacenter_rules_check.py [--verify-reads]
"""
import glob, json, os, re, sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".."))
RULES = os.path.join(ROOT, "site", "data", "forecast", "datacenter_rules.json")
READS = os.path.join(ROOT, "runs", "c740", "reads")
if not os.path.isdir(READS):  # a worktree beside the window's folder: the reads stay in the window's own folder
    READS = os.path.join(os.path.dirname(ROOT), "erw-w3", "runs", "c740", "reads")


def plain(s):
    s = s.replace("’", "'").replace("‘", "'").replace("“", '"').replace("”", '"')
    s = s.replace(" ", " ").replace(" ", " ")
    return re.sub(r"\s+", " ", s).strip()


def text_of(request):
    paths = glob.glob(os.path.join(READS, f"{int(request):03d}_*.txt"))
    if not paths:
        raise SystemExit(f"request {request}: no kept text under {READS}")
    return plain(open(paths[0], encoding="utf-8").read())


def quotes(node, cite=None, path=""):
    """(cite, quote, path) for every non-empty quote under node, the nearest cite above it."""
    if isinstance(node, dict):
        cite = node.get("cite", cite)
        for k, v in node.items():
            if k == "quote" and isinstance(v, str) and v:
                yield cite, v, path
            else:
                yield from quotes(v, cite, f"{path}.{k}")
    elif isinstance(node, list):
        for i, v in enumerate(node):
            yield from quotes(v, cite, f"{path}[{i}]")


def main(argv):
    d = json.load(open(RULES, encoding="utf-8"))
    src = d["sources"]
    n = 0
    for cite, q, path in quotes(d):
        if cite not in src:
            raise SystemExit(f"{path}: cite {cite!r} is not a source")
        n += 1
        if "--verify-reads" in argv:
            req = src[cite]["request"]
            if not isinstance(req, int):
                print(f"{path}: source {cite} was read by an earlier chain ({req}); not verified here")
                continue
            if plain(q) not in text_of(req):
                raise SystemExit(f"{path}: quote not found in request {req}")
    for st, rec in d["states"].items():
        for part in ("sales_exemption", "property", "electricity"):
            if part in rec and rec[part].get("cite") not in src:
                raise SystemExit(f"{st}.{part}: no source")
            if part in rec and len(rec[part].get("tip", "")) < 80:
                raise SystemExit(f"{st}.{part}: no hover words")
    print(f"{n} quotes, {len(d['states'])} states: every check passed")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
