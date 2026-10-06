"""Session 135: the PitchBook accept function, proven on the real database with a throwaway run that is removed.
No PitchBook figure is made up: the payload sent holds an empty company list. Also: the public key reads nothing."""
import json, os, sys
sys.path.insert(0, "warehouse/thesis")
sys.path.insert(0, "scripts")
import run as R
import alert
import requests
from psycopg.types.json import Jsonb

ok = True


def check(name, cond):
    global ok
    ok = ok and bool(cond)
    print(("ok   " if cond else "FAIL ") + name)


c = R.db()
rid, key = "test-accept-0000", "t" * 43
c.execute("delete from public.thesis_runs where run_id = %s", (rid,))
c.execute("insert into public.thesis_runs (run_id, niche, status, pitchbook_key, pitchbook_request) values (%s, 'a throwaway row for the accept proof', 'done', %s, %s)",
          (rid, key, Jsonb({"format": "erw-pitchbook-1", "run_id": rid, "companies": []})))
call = lambda k, p: c.execute("select public.thesis_pitchbook_accept(%s, %s, %s)", (rid, k, Jsonb(p))).fetchone()[0]
good = {"format": "erw-pitchbook-1", "run_id": rid, "pulled_on": "2026-10-06", "label": "PitchBook", "companies": [], "additional_companies": []}
check("a wrong key is refused", call("w" * 43, good) == {"ok": False, "reason": "key"})
check("a short key is refused", call("t" * 10, good) == {"ok": False, "reason": "key"})
check("a payload without a company list is refused and the key is kept", call(key, {"format": "x"}) == {"ok": False, "reason": "shape"})
check("the right key is accepted", call(key, good) == {"ok": True, "companies": 0})
row = c.execute("select pitchbook_key, pitchbook ->> 'label', pitchbook_received_at is not null from public.thesis_runs where run_id = %s", (rid,)).fetchone()
check("the key is erased, the answer is kept on the run with its label", row == (None, "PitchBook", True))
check("the same key a second time is refused", call(key, good) == {"ok": False, "reason": "key"})
check("an unknown run is refused like a wrong key", c.execute("select public.thesis_pitchbook_accept('no-such-run', %s, %s)", (key, Jsonb(good))).fetchone()[0] == {"ok": False, "reason": "key"})

url, anon = alert.env("SUPABASE_URL").rstrip("/"), alert.env("SUPABASE_ANON_KEY")
h = {"apikey": anon, "Authorization": f"Bearer {anon}"}
url = url[:-len("/rest/v1")] if url.endswith("/rest/v1") else url
r = requests.get(f"{url}/rest/v1/thesis_runs?select=run_id&limit=1", headers=h, timeout=30)
check(f"the public key cannot read the table (HTTP {r.status_code}, {r.text[:60]!r})", r.status_code in (401, 403, 404) or r.json() == [])
for fn, args in (("thesis_list", {"p_token": "x" * 30}), ("thesis_get", {"p_token": "x" * 30, "p_run_id": rid}),
                 ("thesis_submit", {"p_token": "x" * 30, "p_niche": "a niche that must not be queued", "p_stage": "", "p_geography": ""})):
    r = requests.post(f"{url}/rest/v1/rpc/{fn}", headers=h, json=args, timeout=30)
    check(f"{fn} with a wrong token answers nothing (HTTP {r.status_code})", r.status_code >= 400 and "not authorized" in r.text)
r = requests.post(f"{url}/rest/v1/rpc/thesis_token_ok", headers=h, json={"p_token": "x"}, timeout=30)
check(f"the token check itself is not callable by the public key (HTTP {r.status_code})", r.status_code >= 400)
n = c.execute("select count(*) from public.thesis_runs where niche = 'a niche that must not be queued'").fetchone()[0]
check("nothing was queued by the wrong token", n == 0)
c.execute("delete from public.thesis_runs where run_id = %s", (rid,))
check("the throwaway row is removed", c.execute("select count(*) from public.thesis_runs where run_id = %s", (rid,)).fetchone()[0] == 0)
print("all pass" if ok else "SOME FAILED")
sys.exit(0 if ok else 1)
