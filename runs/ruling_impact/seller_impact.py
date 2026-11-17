"""Session 7619 (portable-laptop): the ruling impact of the three lines marked "Changes a figure" under
/cost-of-power/seller in docs/reviews/rulings-for-samuel-2026-11-17.md (branch wip/7560-six-reads).

Reads the page's public download (site/public/seller/erw_2026_generator_hourly.csv: the default case, ERCOT solar at the
hub average in real time, per MW, 2018-07 to 2026-10-03) through the page's published Python mirror
(site/public/seller/erw_2026_generator_replication.py), as replication/generator/replicate.py does. No model call.

Line 1: the page ends September 2026 while the builders are off: what the window is now, and what a run would add.
Line 2: "the worst month" from every month held since July 2018, or from the last three years only: merchant (scenario A)
and a contract for all the energy at a fixed price (scenario B, the read's case 3: 200 MW at USD 38 per MWh).
Line 3: the peaker's "Degradation by 1 point" bar: recomputed from the read's peaker margin with the mirror's NPV rule.
"""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PUB = ROOT / "site" / "public" / "seller"
sys.stdout.reconfigure(encoding="utf-8")
spec = importlib.util.spec_from_file_location("mirror", PUB / "erw_2026_generator_replication.py")
M = importlib.util.module_from_spec(spec)
spec.loader.exec_module(M)

rows = M.read(str(PUB / "erw_2026_generator_hourly.csv"))
head = (PUB / "erw_2026_generator_hourly.csv").read_text(encoding="utf-8").splitlines()[:4]
print("\n".join(h[:240] for h in head))

print("\n== line 1: where the page ends")
n = M.numbers(rows)
print(f"last twelve months {n['l12_first']} to {n['l12_last']} ({n['l12_months']} held); months held {n['first_held']} to {n['last_held']} ({n['n']})")
print(f"the headline at the defaults (100 MW): revenue USD {n['l12_kw']:.2f} per kW over the last twelve months; capture rate {n['capture_rate']:.1f} percent; "
      f"coverage {n['cover']:.2f} times; NPV USD {n['npv_million']:.2f} million")
octo = [r for r in rows if r["local_month"] == "2026-10"]
print(f"October 2026 in the file: {len(octo)} hours (the snapshot's last hour 2026-10-03 04:00 UTC); a full month is 744")


def worst(table, mw, price=None, since=None):
    """The worst held month (revenue for mw MW: merchant, or every MWh at price) and its coverage, from `since` on."""
    debt = M.stata_round(M.CAPEX_USD_KW * 1000 * M.DEBT_SHARE * M.DEBT_RATE / (1 - (1 + M.DEBT_RATE) ** (-M.DEBT_YEARS)) * mw)
    out = []
    for m in table:
        if not m["held"] or (since and m["ym"] < since):
            continue
        rev = (m["energy_mwh_per_mw"] * price if price is not None else m["revenue_usd_per_mw"]) * mw
        cover = (rev - M.FOM_USD_KW_YEAR * 1000 * mw / 12) / (debt / 12)
        out.append((rev, m["ym"], cover))
    out.sort()
    return out[0], len(out)


print("\n== line 2: the worst month, every month held against the last three years")
table = n["months"]
for label, mw, price in (("scenario A, merchant, the default 100 MW", 100, None), ("scenario B, all the energy at USD 38, 200 MW (the read's case 3)", 200, 38.0),
                         ("scenario B, all the energy at USD 38, the default 100 MW", 100, 38.0)):
    print(f"-- {label}")
    for since, words in ((None, "every month held (default)"), ("2023-10", "the last three years (2023-10 to 2026-09)"), ("2021-10", "the last five years (2021-10 to 2026-09)")):
        (rev, ym, cover), k = worst(table, mw, price, since)
        print(f"  {words}: {ym}, USD {rev:,.0f}, coverage {cover:.2f} times, of {k} months")

print("\n== line 3: the peaker's 'Degradation by 1 point'")
l12_kw = 43.13      # the read's figure: margin over fuel, USD per kW, 100 MW at HB_HOUSTON, October 2025 to September 2026
for deg in (0.01,):
    loss = sum(l12_kw * (1 - (1 - deg) ** (t - 1)) / (1 + M.HURDLE) ** t for t in range(1, M.LIFE_YEARS + 1)) * 1000 * 100 / 1e6
    print(f"NPV lost to {deg * 100:.0f} point of degradation a year on USD {l12_kw} per kW, 35 years at 12 percent, 100 MW: USD {loss:.2f} million (the page draws 2.38)")
