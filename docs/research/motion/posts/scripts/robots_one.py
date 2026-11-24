"""One robots or terms read, no redirect followed. Session 9900. Usage: robots_one.py <url> <out_file>
Sends only the ERW contact string as User-Agent. Prints status, final address, bytes and the rules without comments."""
import hashlib
import sys
from datetime import datetime, timezone

import requests

UA = "ERW research project, github.com/SamuelEnrique/erw"
url, out = sys.argv[1], sys.argv[2]
at = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
r = requests.get(url, headers={"User-Agent": UA}, timeout=30, allow_redirects=False)
body = r.content
open(out, "wb").write(body)
print(f"read_at={at} status={r.status_code} bytes={len(body)} sha256={hashlib.sha256(body).hexdigest()}")
print(f"location={r.headers.get('Location', '')} content_type={r.headers.get('Content-Type', '')}")
if url.endswith("robots.txt") and r.status_code == 200:
    for line in body.decode("utf-8", "replace").splitlines():
        s = line.split("#", 1)[0].strip()
        if s:
            print(s)
else:
    print(body[:600].decode("utf-8", "replace"))
