"""Session 7616 (portable-laptop): fetch the network's hourly snapshot (the public object erw-public/network/grid_network.json
of the ERW's own Supabase project, which /grid's Network tab and its exchange line read) to runs/ruling_impact/cache/, and
print its shape. Read-only."""
import json
import sys
import urllib.request
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.stdout.reconfigure(encoding="utf-8")
url = next(l.split("=", 1)[1].strip().strip('"') for l in (ROOT / ".env").read_text(encoding="utf-8").splitlines() if l.startswith("SUPABASE_URL="))
origin = "/".join(url.split("/")[:3])
obj = f"{origin}/storage/v1/object/public/erw-public/network/grid_network.json"
data = json.loads(urllib.request.urlopen(obj, timeout=30).read().decode("utf-8"))
(HERE / "cache").mkdir(exist_ok=True)
(HERE / "cache" / "grid_network_snapshot.json").write_text(json.dumps(data), encoding="utf-8")
if __name__ == "__main__":
    print("keys", list(data))
    print("built", data.get("built"), "window", data.get("window"), "hours", len(data["hours"]), data["hours"][0], data["hours"][-1])
    n = data["nodes"][0]
    print("node keys", {k: (type(v).__name__, (len(v) if isinstance(v, list) else v)) for k, v in n.items()})
    print("link keys", list(data["links"][0]))
