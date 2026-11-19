"""Session 8601 (chain 504): writes the test fixture of the map's reader of the whole country's boundary file,
tests/fixtures/session8601/ba_boundaries_contract_fixture.json.

THE SHAPES ARE MADE UP. They are squares placed roughly where a few balancing authorities are, in the form of section 1
of docs/state/page_files_regions.md (a GeoJSON FeatureCollection, one feature a balancing authority), so that the
reader and the map's drawing can be tested before the data machine's file exists and whatever that file holds. They are
not boundaries, they are never shipped with the site, and nothing on a page a person opens is drawn from them.
Run once; the result is committed.

    python tests/fixtures/session8601/make_contract_8601.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def square(w, s, e, n):
    return [[w, s], [e, s], [e, n], [w, n], [w, s]]


def feature(code, name, region, geometry, area):
    return {"type": "Feature", "properties": {"code": code, "name": name, "region": region, "source_id": "fixture-" + code, "area_km2": area, "fixture": "a made-up square, not a boundary"},
            "geometry": geometry}


FEATURES = [
    # a small one first, so the reader has to put the largest first itself
    feature("BANC", "Square for BANC", "CAL", {"type": "Polygon", "coordinates": [square(-121.5, 38, -120.5, 39)]}, 9683.0),
    feature("ERCO", "Square for ERCO", "TEX", {"type": "Polygon", "coordinates": [square(-101, 28, -96, 33)]}, 265989.0),
    # a ring with a hole in its middle: the centroid falls in the hole, so the point inside must be found on a level line
    feature("SWPP", "Ring for SWPP", "CENT", {"type": "Polygon", "coordinates": [square(-102, 34, -95, 40), square(-100, 35.5, -97, 38.5)]}, 414654.0),
    feature("MISO", "Square for MISO", "MIDW", {"type": "Polygon", "coordinates": [square(-94, 38, -88, 46)]}, 441218.0),
    # two parts: the larger part holds the point
    feature("PJM", "Two squares for PJM", "MIDA", {"type": "MultiPolygon", "coordinates": [[square(-84, 37, -76, 41)], [square(-75.5, 39, -75, 39.5)]]}, 307583.0),
    feature("CISO", "Square for CISO", "CAL", {"type": "Polygon", "coordinates": [square(-123, 34, -117, 40)]}, 355428.0),
    # a code the network does not draw: the map leaves it out
    feature("ZZZZ", "Square for no grid of the network", "NW", {"type": "Polygon", "coordinates": [square(-110, 44, -108, 46)]}, 30000.0),
]

FILE = {
    "type": "FeatureCollection",
    "built": "2026-11-19T00:00:00Z",
    "tables": ["ba_boundaries"],
    "method": "docs/methods/grid_network.md",
    "license": "public",
    "source": "TEST FIXTURE: made-up squares, not boundaries",
    "source_url": "fixture://tests/fixtures/session8601/make_contract_8601.py",
    "retrieved_at": "2026-11-19T00:00:00Z",
    "simplify_tolerance_deg": 0.01,
    "bas_without_polygon": ["NYIS", "ISNE"],
    "polygons_without_ba": [{"id": "fixture-stray", "name": "A square that matches no code"}],
    "features": FEATURES,
}

if __name__ == "__main__":
    out = os.path.join(HERE, "ba_boundaries_contract_fixture.json")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump(FILE, f, indent=1)
        f.write("\n")
    print(out, len(FEATURES), "features")
