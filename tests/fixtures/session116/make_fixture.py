"""Session 116: the tests' real sample. For two operating days (6 and 7 December 2025), the rows of 14 resources cut
from ERCOT's own two ESR files as they came in the zips, every column, nothing changed: tests/fixtures/session116/.
Resources are chosen by what their rows show on the 6th, so the sample holds every case the builder tells apart.
No request: the zips are on the disk."""
import csv
import io
import os
import zipfile

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
ZIPS = os.path.join(ROOT, "warehouse", "raw", "ercot_60d_dam", "zips")
OUT = os.path.join(ROOT, "tests", "fixtures", "session116")
DAYS = ["2025-12-06", "2025-12-07"]


def files(day):
    with open(os.path.join(ZIPS, "manifest.csv"), encoding="utf-8", newline="") as f:
        name = [r["file"] for r in csv.DictReader(f) if r["operating_day"] == day][-1]
    z = zipfile.ZipFile(os.path.join(ZIPS, name))
    out = {}
    for n in z.namelist():
        if "60d_DAM_ESR_Data" in n or "60d_DAM_ESR_ASOffers" in n:
            out[n] = z.read(n).decode("utf-8")
    return out


def rows(text):
    r = list(csv.reader(io.StringIO(text)))
    return r[0], r[1:]


first = files(DAYS[0])
data = next(v for k, v in first.items() if "ESR_Data" in k)
offers = next(v for k, v in first.items() if "ASOffers" in k)
h, d = rows(data)
ho, o = rows(offers)
name, status, award = h.index("Resource Name"), h.index("Resource Status"), h.index("Awarded Quantity")
curve = h.index("QSE submitted Curve-MW1")
as_cols = [i for i, c in enumerate(h) if c.strip().endswith("Awarded") and i != award]
offering = {r[ho.index("Resource Name")] for r in o}
listed = sorted({r[name] for r in d})
pick = []


def take(test, n):
    got = [x for x in listed if x not in pick and test([r for r in d if r[name] == x])][:n]
    pick.extend(got)


take(lambda rs: any(r[award] not in ("", "0") for r in rs) and rs[0][name] in offering, 4)        # energy awards and AS offers
take(lambda rs: all(r[award] in ("", "0") for r in rs) and any(r[i] not in ("", "0") for r in rs for i in as_cols), 4)  # AS awards only
take(lambda rs: all(r[curve] == "" for r in rs) and rs[0][name] not in offering and rs[0][status] != "OUT", 2)   # no offer at all, not out
take(lambda rs: all(r[status] == "OUT" for r in rs), 2)                                           # out all day
take(lambda rs: any(r[curve] != "" for r in rs) and rs[0][name] not in offering, 2)               # an energy curve and no AS offer
unlisted = sorted(offering - set(listed))[:1]                                                    # offers and no row in the data file
os.makedirs(OUT, exist_ok=True)
for day in DAYS:
    for fname, text in files(day).items():
        head, body = rows(text)
        i = head.index("Resource Name")
        keep = [r for r in body if r[i] in pick or r[i] in unlisted]
        with open(os.path.join(OUT, fname), "w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(head)
            w.writerows(keep)
        print(day, fname, len(keep), "rows of", len(body))
print("resources:", pick, "unlisted:", unlisted)
