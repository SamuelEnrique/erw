"""Session 10231: the numbers the peak premium explorer's decisions quote, from HB_HUBAVG's 15-minute prices.

    python checks_peak.py <hubavg.csv>
"""
import statistics
import sys

from restate_peak import load_prices, pct

rt = load_prices(sys.argv[1], "spp_rtm")
for y in (2020, 2021, 2022, 2023, 2024, 2025):
    v = [x for _, l, x in rt if l.year == y]
    print(f"{y}: plain mean {statistics.fmean(v):.4f}, median {pct(sorted(v), 50):.4f}, n {len(v)}")
feb = [x for _, l, x in rt if l.year == 2021 and l.month == 2]
yr = [x for _, l, x in rt if l.year == 2021]
print(f"2021: intervals at or above 1,000: {sum(1 for x in yr if x >= 1000)} in the year, {sum(1 for x in feb if x >= 1000)} in February")
print(f"2021: 99.9th percentile of the year {pct(sorted(yr), 99.9):.4f}; without February {pct(sorted([x for _, l, x in rt if l.year == 2021 and l.month != 2]), 99.9):.4f}")
# where the year's highest interval sits
for y in (2015, 2025):
    t, l, x = max(((t, l, x) for t, l, x in rt if l.year == y), key=lambda r: r[2])
    print(f"{y}: highest interval {x} at {l} local (hour {l.hour})")
