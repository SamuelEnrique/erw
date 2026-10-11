"""Session 187: the raw files' handover through the archive bucket (scripts/raw_handover.py).

A folder tree is cut into parts, packed into a store in memory, and fetched into another folder: every file comes out
byte for byte, a file larger than a part travels as slices, nothing on the sending side changes, a second upload sends
nothing, an object is never replaced, and a file already on the receiving machine with other bytes is never overwritten.
"""
import hashlib
import importlib.util
import json
import os
import tempfile
import unittest

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location("raw_handover_187", os.path.join(HERE, "..", "scripts", "raw_handover.py"))
H = importlib.util.module_from_spec(spec)
spec.loader.exec_module(H)

CAP = 64 * 1024


def tree(root):
    """{path under root: sha256}, every file."""
    out = {}
    for d, _, fs in os.walk(root):
        for f in fs:
            p = os.path.join(d, f)
            out[os.path.relpath(p, root).replace(os.sep, "/")] = hashlib.sha256(open(p, "rb").read()).hexdigest()
    return out


def write(root, rel, data):
    p = os.path.join(root, *rel.split("/"))
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "wb") as f:
        f.write(data)


class RawHandover(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.raw = os.path.join(self.tmp.name, "raw")
        self.work = os.path.join(self.tmp.name, "work")
        os.makedirs(self.work)
        for i in range(40):                                            # many small files: several tar parts
            write(self.raw, f"zone_price_history/nyiso/day_{i:03d}.csv", (f"a,b\n{i},{i * 7}\n" * 400).encode())
        write(self.raw, "ercot_zone_prices/dam_2015.zip", os.urandom(30_000))       # stored, not compressed
        write(self.raw, "ercot_zone_prices/big_2016.zip", os.urandom(3 * CAP + 123))   # larger than a part: slices
        write(self.raw, "ercot_zone_prices/counts.json", b'{"n": 1}')
        write(self.raw, "alpha/" + "d" * 60 + "/" + "n" * 70 + ".txt", b"a long name\n" * 10)
        write(self.raw, "alpha/empty.txt", b"")
        write(self.raw, "alpha/__pycache__/x.pyc", b"cache")
        write(self.raw, "madeup_as_prices/20261004T034123Z/manifest.csv", b"made up\n")
        self.plan = H.make_plan(self.raw, cap=CAP)
        self.state = os.path.join(self.work, "state.jsonl")
        self.store = H.DictStore()

    def tearDown(self):
        self.tmp.cleanup()

    def handover(self):
        return H.write_handover(self.store, self.plan, self.state, os.path.join(self.work, "handover.json"), machine="test")

    def test_plan_order_and_what_is_left_out(self):
        self.assertEqual([f["folder"] for f in self.plan["folders"]], ["ercot_zone_prices", "zone_price_history", "alpha"])
        self.assertEqual(sorted(x["path"] for x in self.plan["left_out"]), ["alpha/__pycache__", "madeup_as_prices"])
        paths = [f[0] for p in self.plan["parts"] if p["kind"] == "tar" for f in p["files"]]
        self.assertFalse([p for p in paths if "madeup" in p or "__pycache__" in p])
        big = [p for p in self.plan["parts"] if p["kind"] == "chunk"]
        self.assertEqual([(p["index"], p["of"]) for p in big], [(1, 4), (2, 4), (3, 4), (4, 4)])
        self.assertFalse(big[0]["gz"])                                  # a zip is stored as it is
        self.assertTrue(all(not p["object"].endswith(".csv.gz") for p in self.plan["parts"]))   # the archive reads only those
        self.assertTrue(all(p["object"].count("/") >= 4 for p in self.plan["parts"]))

    def test_round_trip_byte_for_byte(self):
        before = tree(self.raw)
        ok, failed, left = H.upload(self.store, self.plan, self.state, raw=self.raw, workers=2)
        self.assertEqual((failed, left), ([], 0))
        self.assertEqual(ok, len(self.plan["parts"]))
        self.assertEqual(tree(self.raw), before)                        # nothing changed on the sending side
        self.assertTrue(all(len(b) <= CAP + 20_000 for b in self.store.objects.values()))
        h = self.handover()
        self.assertTrue(h["complete"])
        dest = os.path.join(self.tmp.name, "dest")
        n = H.fetch(self.store, h, dest=dest, state_path=os.path.join(self.work, "fetch.jsonl"),
                    conflicts_path=os.path.join(self.work, "conflicts.csv"))
        self.assertEqual((n["bad_parts"], n["conflict"]), (0, 0))
        expected = {k: v for k, v in before.items() if "madeup" not in k and "__pycache__" not in k}
        self.assertEqual(tree(dest), expected)
        same, missing, different = H.verify(self.store, h, dest=dest)
        self.assertEqual((same, missing, different), (len(expected), [], []))
        self.assertEqual(h["raw"]["files_uploaded"], len(expected))
        # the file's time travels with it
        a = os.path.join(self.raw, "ercot_zone_prices", "counts.json")
        b = os.path.join(dest, "ercot_zone_prices", "counts.json")
        self.assertEqual(int(os.stat(a).st_mtime), int(os.stat(b).st_mtime))
        c = os.path.join(self.raw, "ercot_zone_prices", "big_2016.zip")
        d = os.path.join(dest, "ercot_zone_prices", "big_2016.zip")
        self.assertEqual(int(os.stat(c).st_mtime), int(os.stat(d).st_mtime))
        # a second fetch reads nothing
        again = H.fetch(self.store, h, dest=dest, state_path=os.path.join(self.work, "fetch.jsonl"),
                        conflicts_path=os.path.join(self.work, "conflicts.csv"))
        self.assertEqual(again["parts"], 0)

    def test_upload_resumes_and_never_replaces(self):
        ok1, failed, left = H.upload(self.store, self.plan, self.state, raw=self.raw, workers=2, only={"ercot_zone_prices"})
        self.assertEqual(failed, [])
        held = dict(self.store.objects)
        ok2, failed, left = H.upload(self.store, self.plan, self.state, raw=self.raw, workers=2)
        self.assertEqual(ok1 + ok2, len(self.plan["parts"]))
        self.assertTrue(all(self.store.objects[k] == v for k, v in held.items()))
        ok3, failed, left = H.upload(self.store, self.plan, self.state, raw=self.raw, workers=2)
        self.assertEqual((ok3, failed, left), (0, [], 0))
        # the state lost, the objects still there: the same bytes are taken as uploaded, not sent over them
        os.remove(self.state)
        ok4, failed, left = H.upload(self.store, self.plan, self.state, raw=self.raw, workers=2)
        self.assertEqual((ok4, failed), (len(self.plan["parts"]), []))
        self.assertTrue(all(json.loads(x)["put"] == "exists" for x in open(self.state, encoding="utf-8")))
        with self.assertRaises(RuntimeError):
            self.store.put(self.plan["parts"][0]["object"], b"other bytes")

    def test_half_uploaded_handover_says_so(self):
        H.upload(self.store, self.plan, self.state, raw=self.raw, workers=2, only={"ercot_zone_prices"})
        h = self.handover()
        self.assertFalse(h["complete"])
        done = {f["folder"]: f["complete"] for f in h["raw"]["folders"]}
        self.assertEqual(done, {"ercot_zone_prices": True, "zone_price_history": False, "alpha": False})
        self.assertEqual(h["raw"]["manifest"]["rows"], 3)

    def test_a_file_already_there_is_never_overwritten(self):
        H.upload(self.store, self.plan, self.state, raw=self.raw, workers=2)
        h = self.handover()
        dest = os.path.join(self.tmp.name, "dest")
        write(dest, "ercot_zone_prices/counts.json", b'{"n": 2, "mine": true}')
        write(dest, "zone_price_history/nyiso/day_000.csv", open(os.path.join(self.raw, "zone_price_history", "nyiso", "day_000.csv"), "rb").read())
        conflicts = os.path.join(self.work, "conflicts.csv")
        n = H.fetch(self.store, h, dest=dest, state_path=os.path.join(self.work, "fetch.jsonl"), conflicts_path=conflicts)
        self.assertEqual((n["conflict"], n["same"]), (1, 1))
        self.assertEqual(open(os.path.join(dest, "ercot_zone_prices", "counts.json"), "rb").read(), b'{"n": 2, "mine": true}')
        self.assertIn("ercot_zone_prices/counts.json", open(conflicts, encoding="utf-8").read())
        same, missing, different = H.verify(self.store, h, dest=dest)
        self.assertEqual(different, ["ercot_zone_prices/counts.json"])

    def test_a_damaged_part_writes_nothing(self):
        H.upload(self.store, self.plan, self.state, raw=self.raw, workers=2, only={"alpha"})
        h = self.handover()
        obj = [f for f in h["raw"]["folders"] if f["folder"] == "alpha"][0]["parts"][0]["object"]
        body = self.store.objects[obj]
        self.store.objects[obj] = body[:-1] + bytes([body[-1] ^ 0xFF])
        dest = os.path.join(self.tmp.name, "dest")
        n = H.fetch(self.store, h, dest=dest, state_path=os.path.join(self.work, "fetch.jsonl"),
                    conflicts_path=os.path.join(self.work, "conflicts.csv"), folders={"alpha"})
        self.assertEqual(n["bad_parts"], 1)
        self.assertEqual(tree(dest), {})

    def test_a_path_that_leaves_the_folder_is_refused(self):
        for rel in ("../x", "a/../../x", "/etc/x", "C:/x"):
            with self.assertRaises(RuntimeError):
                H.safe_target(self.tmp.name, rel)


if __name__ == "__main__":
    unittest.main()
