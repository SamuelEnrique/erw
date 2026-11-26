# Session 10233: the method notes in this morning's content bundle (site/content/docs.json) against docs/methods/ now,
# and the /data page's drawn method links against both.
#   python runs/c10233/docs_methods.py <worktree> <draw prefix>
import json
import os
import re
import sys

ROOT, PREFIX = sys.argv[1:3]
d = json.load(open(os.path.join(ROOT, "site", "content", "docs.json"), encoding="utf-8"))
bundle = set(d["methods"])
INTERNAL = {"thesis_builder", "digest_scoring", "roundup_selection", "forecast"}
now = {f[:-3] for f in os.listdir(os.path.join(ROOT, "docs", "methods")) if f.endswith(".md")} - INTERNAL
html = open(PREFIX + "_data.html", encoding="utf-8").read()
sec = html[html.find('id="methods"'):]
linked = set(re.findall(r'href="/data/methods/([\w-]+)"', sec))
items = re.findall(r"<li>(.*?)</li>", sec, flags=re.S)
print(f"bundle {len(bundle)}; docs/methods now {len(now)}; only now {sorted(now - bundle)}; only bundle {sorted(bundle - now)}")
print(f"methodology list items drawn {len(items)}; linked {len(linked)}; bundled but not linked {sorted(bundle - linked)[:20]}")
