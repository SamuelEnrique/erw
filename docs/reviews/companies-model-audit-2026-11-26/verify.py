"""Checks of sentences in the audit document against the drawings and the main copy's NYISO queue file. Session
10228. Prints each check and its result."""
import csv
import io
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
D = os.path.join(HERE, "draw")


def text(name):
    return open(os.path.join(D, f"main_{name}.txt"), encoding="utf-8").read()


for name, needle in (("fpl", "utility, gas, in FL, TX, CA, GA. 475 public rows of 7 tables name it."),
                     ("fpl", "gas 26,891 65.9%"), ("fpl", "solar 8,829 21.6%"), ("fpl", "nuclear 3,914 9.6%"),
                     ("fpl", "storage 1,015 2.5%"), ("fpl", "oil 166 0.4%"), ("fpl", "other 3 0.0%"),
                     ("fpl", "1958-11-01 to 2027-10-01 (planned)"), ("fpl", "1,148"), ("fpl", "3,666 MW as the NRC states them"),
                     ("ceg", "25 public rows of 2 tables name it"), ("ceg", "Constellation Energy Corporation"),
                     ("index_policy", "0 of 12,724 companies match"), ("google", "27 rows of energy_deals name this company")):
    print(name, "|", needle, "|", needle in text(name))
p = r"C:\Users\lossa\Documents\erw\warehouse\output\nyiso_interconnection_queue.csv"
lines = [ln for ln in open(p, encoding="utf-8") if not ln.startswith("#")]
rows = list(csv.DictReader(io.StringIO("".join(lines))))
print("nyiso rows", len(rows), "with operator", sum(1 for r in rows if (r.get("operator") or "").strip()))
for h in open(p, encoding="utf-8"):
    if h.startswith("#") and ("etriev" in h or "Source" in h):
        print("HDR", h.strip()[:200])
    if not h.startswith("#"):
        break
