"""Window D's data request 55 (the reports audit, finding 2): from the live set, cost_of_power_monthly's newest month with a
da_shape_premium row for CAISO TH_SP15_GEN-APND, ERCOT HB_HUBAVG and SPP SPPNORTH_HUB, with da_shape_premium, da_hours and
hours_in_month; the latest month whole at all three; cost_of_power_hourly_profile's newest month with each hub's
rt_days_h12. Read only over SUPABASE_DB_URL."""
import psycopg

url = [ln.split("=", 1)[1].strip().strip('"') for ln in open(".env", encoding="utf-8") if ln.startswith("SUPABASE_DB_URL=")][0]
con = psycopg.connect(url, connect_timeout=30)
con.read_only = True
cur = con.cursor()
cur.execute("select column_name from information_schema.columns where table_name = 'series' order by ordinal_position")
print("series columns:", [r[0] for r in cur.fetchall()])
for t in ("cost_of_power_monthly", "cost_of_power_hourly_profile"):
    cur.execute("select distinct entity from series where table_name = %s order by 1 limit 40", (t,))
    print(t, "entities:", [r[0] for r in cur.fetchall()][:20])
    cur.execute("select distinct variable from series where table_name = %s order by 1", (t,))
    print(t, "variables:", [r[0] for r in cur.fetchall()][:40])
con.close()
con = psycopg.connect(url, connect_timeout=30)
con.read_only = True
cur = con.cursor()
HUBS = ["caiso:TH_SP15_GEN-APND", "ercot:HB_HUBAVG", "spp:SPPNORTH_HUB"]
latest = {}
for h in HUBS:
    cur.execute("select max(ts_utc) from series where table_name='cost_of_power_monthly' and entity=%s and variable='da_shape_premium'", (h,))
    m = cur.fetchone()[0]
    cur.execute("select variable, value, loaded_at from series where table_name='cost_of_power_monthly' and entity=%s and ts_utc=%s "
                "and variable in ('da_shape_premium','da_hours','hours_in_month')", (h, m))
    print("==", h, "newest month with da_shape_premium:", m, {r[0]: r[1] for r in cur.fetchall()})
    cur.execute("""select max(a.ts_utc) from series a join series b on b.table_name=a.table_name and b.entity=a.entity and b.ts_utc=a.ts_utc
                   where a.table_name='cost_of_power_monthly' and a.entity=%s and a.variable='da_hours' and b.variable='hours_in_month' and a.value=b.value""", (h,))
    latest[h] = cur.fetchone()[0]
    cur.execute("select max(ts_utc) from series where table_name='cost_of_power_hourly_profile' and entity=%s and variable='rt_days_h12'", (h,))
    pm = cur.fetchone()[0]
    cur.execute("select value from series where table_name='cost_of_power_hourly_profile' and entity=%s and variable='rt_days_h12' and ts_utc=%s", (h, pm))
    print("   newest whole month (da_hours = hours_in_month):", latest[h], "| profile newest month:", pm, "rt_days_h12:", cur.fetchone()[0])
w = min(latest.values())
print("latest month whole at all three:", w)
for h in HUBS:
    cur.execute("select variable, value from series where table_name='cost_of_power_monthly' and entity=%s and ts_utc=%s "
                "and variable in ('da_shape_premium','da_hours','hours_in_month')", (h, w))
    print("  ", h, {r[0]: r[1] for r in cur.fetchall()})
con.close()
