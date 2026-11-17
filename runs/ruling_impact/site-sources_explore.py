"""Session 7614 (portable-laptop): which ERCOT price tables of the live set hold 5 to 11 November 2026, hours or rows a day."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from live import q  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")
names = [r[0] for r in q("select distinct table_name from public.series where entity like 'ercot:%' and ts_utc >= '2026-11-01'")]
for t in sorted(names):
    rows = q("select (ts_utc at time zone 'America/Chicago')::date d, count(*) from public.series where table_name=%s and entity like 'ercot:%%' "
             "and ts_utc >= '2026-11-04 06:00+00' and ts_utc < '2026-11-13 06:00+00' group by 1 order by 1", (t,))
    print(t, " ".join(f"{d:%m-%d}:{n}" for d, n in rows))
