"""Session 10213: an expert's expected capacity: each grid and technology's active MW times its own past share of MW
that reached operation (2000 to 2020), from the page's file alone.

    python measures3_queues.py <queues.json>
"""
import json
import sys

qj = json.load(open(sys.argv[1], encoding="utf-8"))
grids = ["caiso", "ercot", "isone", "miso", "nyiso", "pjm", "spp", "west", "southeast"]
techs = ["solar", "solar_battery", "battery", "wind", "offshore_wind", "gas", "other"]
exp_mw = exp_n = act = no_share = 0.0
by_grid = {}
for g in grids:
    ge = ga = 0.0
    for t in techs:
        v = qj["views"].get(f"{g}|{t}")
        if not v:
            continue
        w = v["whole"]
        a = w["total_active_mw"]
        act += a
        ga += a
        s = w.get("past_mw_operating_share_pct")
        if s is None:
            s = qj["views"][f"{g}|all"]["whole"].get("past_mw_operating_share_pct")
            no_share += a
        exp_mw += a * s / 100
        ge += a * s / 100
        sn = w.get("past_operating_share_pct") or qj["views"][f"{g}|all"]["whole"].get("past_operating_share_pct")
        exp_n += w["total_active_requests"] * sn / 100
    by_grid[g] = (round(ga), round(ge), round(100 * ge / ga, 1))
print(f"active MW {act:,.0f}; expected to reach operation at each grid and technology's past share by MW: {exp_mw:,.0f} MW ({100 * exp_mw / act:.1f} percent); "
      f"active MW whose view has no share (the grid's every-technology share used): {no_share:,.0f}")
print(f"active requests {qj['views']['us|all']['whole']['total_active_requests']:,}; expected by count: {exp_n:,.0f}")
print("by grid (active MW, expected MW, percent):", by_grid)
