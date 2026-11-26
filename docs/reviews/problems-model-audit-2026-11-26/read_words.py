"""Session 10229: read every new sentence of the five words branches in the drawn pages of the merged branch, and the old
ones gone. Pass when each new sentence is found where it belongs and no old one is left."""
import sys
from pathlib import Path

d = Path(sys.argv[1])
pages = {
    "bill set (kept reads)": d / "words_kept_prices-and-your-bill.txt",
    "trade": d / "words_draw" / "page_who-trades-with-whom.txt",
    "storm": d / "words_draw" / "page_storm-across-the-country.txt",
    "ground": d / "words_draw" / "page_under-the-ground-and-in-the-wind.txt",
    "industry": d / "words_draw" / "page_where-energy-goes.txt",
    "authority": d / "words_draw" / "page_your-own-balancing-authority.txt",
}
new = {
    "bill set (kept reads)": ["taxes and local fees are not on it", "Value the kWh on the meter, with no losses added, at the load-weighted real-time price of the CAISO NP15 in the latest complete month, 2026-09.",
                               "at the load-weighted real-time price of the ERCOT hub average in the latest complete month, 2026-09.", "The wholesale energy is the smaller part of a home's bill.",
                               "in Texas the retailer's energy charge alone is more than half the default bill", "Every answer is computed from the warehouse's tables when the page is built",
                               "Each answer is computed from the unrounded figures"],
    "trade": ["Tennessee's report was how many times the Southeast's?", "Tennessee's report was how many times the Midwest's?", "its 2025 flow was how many times its 2019 flow?",
              "the sum of the neighbours' figures above.", "Every answer is computed from committed page files", "Each answer is computed from the unrounded figures"],
    "storm": ["imports carried much of the rest (the question on the flows into Tennessee)", "Every answer is computed from committed page files"],
    "ground": ["The answer divides the list's own values, which hold more decimals than the legend prints", "The legend prints it to one decimal; the answer subtracts the list's own value"],
    "industry": ["Every answer is computed from committed page files"],
    "authority": ["how much did its average demand grow from 2019 to 2025", "the newest whole year's average demand against 2019's"],
}
old = ["not the power itself", "how many times the Southeast's report was Tennessee's", "how many times the Midwest's report was Tennessee's", "how many times its 2019 flow was its 2025 flow",
       "the sum of the four", "such as gas, coal and hydro.", "how much did its demand grow"]
ok = True
for name, path in pages.items():
    text = path.read_text(encoding="utf-8")
    for s in new[name]:
        found = s in text
        ok &= found
        print(f"{'found' if found else 'MISSING'}  {name}: {s}")
    for s in old:
        if s in text:
            ok = False
            print(f"OLD LEFT  {name}: {s}")
    print(f"  {name}: em dashes {text.count(chr(0x2014))}")
    ok &= text.count(chr(0x2014)) == 0
print("pass" if ok else "fail")
