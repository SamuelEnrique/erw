"""Window D's data request 37 (the AI energy audit): three reads of the saved publications in
warehouse/raw/ai_energy_published/20261119T1230Z/, quotes and pages only. Pages are the text files' form feeds (pdftotext
writes one between pages). Prints each search's hits with its page and the sentence around it."""
import re
import sys

D = "runs/c701/ai_paged/"  # pdftotext of the saved PDFs, a form feed between pages


def hits(name, pattern, width=260, most=6):
    t = open(D + name, encoding="utf-8", errors="replace").read()
    pages = t.split("\f")
    n = 0
    for i, p in enumerate(pages, 1):
        flat = re.sub(r"\s+", " ", p)
        for m in re.finditer(pattern, flat, re.I):
            print(f"  {name} p.{i}: ...{flat[max(0, m.start() - width // 2):m.end() + width // 2]}...")
            n += 1
            if n >= most:
                return
    if not n:
        print(f"  {name}: no match for {pattern!r} ({len(pages)} pages)")


print("== (1) a venue printed")
for f in ("bloom_2022.txt",):
    hits(f, r"Journal of Machine Learning Research|JMLR|Machine Learning Research", most=3)
for f in ("patterson_2022.txt",):
    hits(f, r"IEEE Computer|\bComputer\b.{0,40}(IEEE|vol|issue)|IEEE Computer Society|Published in", most=4)
print("== (2) patterson_2022: machine learning's share of Google's energy; the Evolved Transformer against Strubell")
hits("patterson_2022.txt", r"(10|15)%.{0,80}(energy|ML)|share of .{0,40}energy|ML (workloads|training).{0,60}(percent|%)", most=6)
hits("patterson_2022.txt", r"Evolved Transformer|Strubell", most=8)
print("== (3) the geography of the electricity tables")
hits("microsoft_2026_fact_sheet.txt", r"global|United States|U\.S\.|worldwide|by country|region|geograph", most=8)
hits("meta_2025_data_index.txt", r"global|United States|U\.S\.|worldwide|by country|region|geograph|data center locations", most=8)
