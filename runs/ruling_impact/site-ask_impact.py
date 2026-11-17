"""Session 7611 (portable-laptop): the ruling impact of the four lines marked "Changes a figure" under
"Site-wide: Ask (the chat)" in docs/reviews/rulings-for-samuel-2026-11-17.md (branch wip/7560-six-reads).

Reads the live set (Supabase, read-only) as the chat's tools read it: the tables the chat answers from. No model call.
Prints each line's figure under the default and under the other choice, and the change in units and percent.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from live import q, retrieved  # noqa: E402

sys.stdout.reconfigure(encoding="utf-8")


def pct(a, b):
    return "n/a" if not a else f"{(b - a) / a * 100:+.2f} percent"


print("== provenance")
for shape, t in [("entities", "spp_interconnection_queue"), ("entities", "lbnl_interconnection_queue"),
                 ("series", "hub_price_comparison"), ("series", "iso_dam_hub_prices"), ("series", "iso_trader_daily"),
                 ("series", "price_board_spreads")]:
    r = retrieved(shape, t)
    print(f"{t}: latest retrieved {r[0]}, source {r[1]}")

print("\n== line 1: SPP's withdrawn queue, summed (landing row 14 of the old laptop)")
n, mw = q("select count(*), sum(capacity_mw) from public.entities where table_name='spp_interconnection_queue' and status='withdrawn'")[0]
print(f"now, the table read whole (the fix, landed): {n} withdrawn requests, {mw:,.3f} MW")
wrong, right14 = 419388.735, 419636.335
print(f"14 November (docs/methods/ask.md, session 6192): the paged read gave {wrong:,.3f} MW where the rows summed to {right14:,.3f}: "
      f"{wrong - right14:+,.3f} MW, {pct(right14, wrong)}")

print("\n== line 2: Berkeley Lab's queue figures for a held grid's region")
regions = ("ISO-NE", "NYISO", "MISO")
tot = q("select count(*), sum(capacity_mw) from public.entities where table_name='lbnl_interconnection_queue'")[0]
act = q("select count(*), sum(capacity_mw) from public.entities where table_name='lbnl_interconnection_queue' and extra->>'q_status'='active'")[0]
print(f"whole table: {tot[0]} rows, {tot[1]:,.1f} MW; active {act[0]} rows, {act[1]:,.1f} MW")
held_rows = held_mw = held_act_rows = held_act_mw = 0
for reg in regions:
    rows = q("select extra->>'q_status', count(*), sum(capacity_mw) from public.entities where table_name='lbnl_interconnection_queue' "
             "and extra->>'region'=%s group by 1 order by 1", (reg,))
    cells = "; ".join(f"{s} {c} rows {m:,.1f} MW" for s, c, m in rows)
    print(f"{reg}: {cells}")
    for s, c, m in rows:
        held_rows += c
        held_mw += m
        if s == "active":
            held_act_rows += c
            held_act_mw += m
print(f"the three regions: {held_rows} rows ({held_rows / tot[0] * 100:.1f} percent of the table), {held_mw:,.1f} MW; active {held_act_rows} rows, {held_act_mw:,.1f} MW")
print(f"a national active total over Berkeley Lab's table: {act[1]:,.1f} MW with them, {act[1] - held_act_mw:,.1f} MW without: "
      f"{-held_act_mw:+,.1f} MW, {pct(act[1], act[1] - held_act_mw)}")

print("\n== line 3: a spread across two grids in Ask ERCOT (CAISO's SP15 less ERCOT's hub average)")
m = dict(q("select entity, value from public.series where table_name='hub_price_comparison' and freq='P1M' and variable='dam_avg_price' "
           "and ts_utc='2026-10-01' and entity in ('caiso:TH_SP15_GEN-APND','ercot:HB_HUBAVG')"))
sp, hb = m["caiso:TH_SP15_GEN-APND"], m["ercot:HB_HUBAVG"]
print(f"October 2026, day-ahead, monthly table: SP15 {sp:.2f}, ERCOT hub average {hb:.2f}, SP15 less ERCOT {sp - hb:+.2f} USD/MWh")
r = dict(q("select entity, value from public.series where table_name='hub_price_comparison' and freq='P1M' and variable='rtm_avg_price' "
           "and ts_utc='2026-10-01' and entity in ('caiso:TH_SP15_GEN-APND','ercot:HB_HUBAVG')"))
print(f"October 2026, real time, monthly table: SP15 {r['caiso:TH_SP15_GEN-APND']:.2f}, ERCOT hub average {r['ercot:HB_HUBAVG']:.2f}, "
      f"SP15 less ERCOT {r['caiso:TH_SP15_GEN-APND'] - r['ercot:HB_HUBAVG']:+.2f} USD/MWh")
d = q("select a.ts_utc::date, a.value - b.value from public.series a join public.series b on a.ts_utc=b.ts_utc "
      "where a.table_name='price_board_spreads' and b.table_name='price_board_spreads' and a.variable='da_daily_mean' and b.variable='da_daily_mean' "
      "and a.entity='caiso:TH_SP15_GEN-APND' and b.entity='ercot:HB_HUBAVG' order by 1")
octd = [v for t, v in d if t.year == 2026 and t.month == 10]
print(f"the board's daily means: {len(d)} common days, latest {d[-1][0]} {d[-1][1]:+.2f}; October {len(octd)} days, mean of the daily spreads {sum(octd) / len(octd):+.2f} USD/MWh")

print("\n== line 4: October's day-ahead average at SP15 from two tables")
h = q("select count(*), avg(value), min(ts_utc), max(ts_utc) from public.series where table_name='iso_dam_hub_prices' and entity='caiso:TH_SP15_GEN-APND' "
      "and ts_utc >= '2026-10-01 07:00+00' and ts_utc < '2026-11-01 07:00+00'")[0]
print(f"hourly table iso_dam_hub_prices, October (Pacific days): {h[0]} hours held, mean {h[1]:.2f} USD/MWh ({h[2]} to {h[3]})")
hu = q("select count(*), avg(value) from public.series where table_name='iso_dam_hub_prices' and entity='caiso:TH_SP15_GEN-APND' "
       "and ts_utc >= '2026-10-01 00:00+00' and ts_utc < '2026-11-01 00:00+00'")[0]
print(f"the same by UTC days: {hu[0]} hours, mean {hu[1]:.2f}")
mh = dict(q("select variable, value from public.series where table_name='hub_price_comparison' and freq='P1M' and ts_utc='2026-10-01' "
            "and entity='caiso:TH_SP15_GEN-APND' and variable in ('dam_avg_price','dam_hours_held')"))
print(f"monthly table hub_price_comparison: {mh['dam_avg_price']:.2f} USD/MWh over {mh['dam_hours_held']:.0f} hours held")
td = q("select count(*), avg(value) from public.series where table_name='iso_trader_daily' and entity='caiso:TH_SP15_GEN-APND' and variable='da_mean_usd' "
       "and ts_utc >= '2026-10-01' and ts_utc < '2026-11-01'")[0]
print(f"daily table iso_trader_daily: {td[0]} days held in October, mean of daily means {td[1]:.2f}")
bd = q("select count(*), avg(value) from public.series where table_name='price_board_spreads' and entity='caiso:TH_SP15_GEN-APND' and variable='da_daily_mean' "
       "and ts_utc >= '2026-10-01' and ts_utc < '2026-11-01'")[0]
print(f"board table price_board_spreads: {bd[0]} days held in October, mean of daily means {bd[1]:.2f}")
print(f"the hourly window against the whole month: {h[1]:.2f} to {mh['dam_avg_price']:.2f}: {mh['dam_avg_price'] - h[1]:+.2f} USD/MWh, {pct(h[1], mh['dam_avg_price'])}")
print(f"14 November's pair (note_2026-11-14_portable_p3.md ruling 6): 41.81 over 543 hours against 46.78: {46.78 - 41.81:+.2f}, {pct(41.81, 46.78)}")
