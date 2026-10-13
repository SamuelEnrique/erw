"""Session 251 (after session 252's fetch_drafts.py): read every row of public.scanner_drafts (a read; no row is written) and keep each draft's row and
files under runs/session251/drafts/<id>/. Prints one line a draft: id, rule, state, raised_at, strength, files."""
import base64
import json
import os
import sys
import urllib.parse

import requests

ROOT = os.path.dirname(os.path.abspath(__file__))
while not os.path.exists(os.path.join(ROOT, "ARCHITECTURE.md")):   # the repository root, from runs/ or from docs/
    ROOT = os.path.dirname(ROOT)
sys.path.insert(0, os.path.join(ROOT, "warehouse"))
import lock  # noqa: E402

OUT = os.path.join(ROOT, "runs", "session251", "drafts")
url, key = lock.env("SUPABASE_URL"), lock.env("SUPABASE_SERVICE_KEY")
u = urllib.parse.urlparse(url)
base = f"{u.scheme}://{u.netloc}/rest/v1/scanner_drafts"
h = {"apikey": key, "Authorization": f"Bearer {key}"}
r = requests.get(base, params={"select": "id,rule,state,raised_at,state_at,strength,flag_key,table_name,series_key,flag_date,value,scanner_version",
                               "order": "raised_at.asc", "limit": "5000"}, headers=h, timeout=60)
r.raise_for_status()
rows = r.json()
print(f"{len(rows)} rows in scanner_drafts")
index = []
for x in rows:
    d = os.path.join(OUT, x["id"])
    os.makedirs(d, exist_ok=True)
    q = requests.get(base, params={"select": "*", "id": f"eq.{x['id']}"}, headers=h, timeout=120)
    q.raise_for_status()
    full = q.json()[0]
    files = full.pop("files", None) or {}
    with open(os.path.join(d, "row.json"), "w", encoding="utf-8", newline="\n") as f:
        json.dump(full, f, indent=1, ensure_ascii=False)
        f.write("\n")
    for name, body in files.items():
        p = os.path.join(d, name)
        if body.get("kind") == "png":
            with open(p, "wb") as f:
                f.write(base64.b64decode(body["content"]))
        else:
            with open(p, "w", encoding="utf-8", newline="\n") as f:
                f.write(body["content"])
    index.append({**x, "files": sorted(files)})
    print(f"{x['id']}  {x['rule']:<10} {x['state']:<16} raised {x['raised_at'][:19]}  strength {x['strength']}  "
          f"table {x['table_name']}  key {x['series_key']}  files {len(files)}")
with open(os.path.join(OUT, "index.json"), "w", encoding="utf-8", newline="\n") as f:
    json.dump(index, f, indent=1)
    f.write("\n")
