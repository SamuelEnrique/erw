"""Session 180: writes the test fixture of the boundary builder, tests/fixtures/session180/squares.geojson.

THE SHAPES ARE MADE UP. They are squares placed roughly where a few balancing authorities are, so that the builder and
the map's drawing can be tested without a publisher's file. They are not boundaries, they are never shipped with the
site, and nothing on a page is drawn from them. Run once; the result is committed.

    python tests/fixtures/session180/make_squares_180.py
"""
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))


def square(w, s, e, n):
    return [[[w, s], [e, s], [e, n], [w, n], [w, s]]]


def feature(code, name, geometry):
    return {"type": "Feature", "properties": {"BA_CODE": code, "NAME": name, "fixture": "a made-up square, not a boundary"}, "geometry": geometry}


FEATURES = [
    # one balancing authority in two features (the builder joins them) with a speck that the simplification drops
    feature("ERCO", "Square for ERCO, west half", {"type": "Polygon", "coordinates": square(-101, 28, -98.5, 33)}),
    feature("ERCO", "Square for ERCO, east half", {"type": "MultiPolygon", "coordinates": [square(-98.5, 28, -96, 33), square(-95.5, 28, -95.499, 28.001)]}),
    feature("SWPP", "Square for SWPP", {"type": "Polygon", "coordinates": square(-102, 34, -95, 40)}),
    feature("MISO", "Square for MISO", {"type": "Polygon", "coordinates": square(-94, 38, -88, 46)}),
    feature("PJM", "Square for PJM", {"type": "Polygon", "coordinates": square(-84, 37, -76, 41)}),
    feature("CISO", "Square for CISO", {"type": "Polygon", "coordinates": square(-123, 34, -117, 40)}),
    # a balancing authority inside another: drawn on top of it
    feature("BANC", "Square for BANC, inside the square for CISO", {"type": "Polygon", "coordinates": square(-121.5, 38, -120.5, 39)}),
    feature("BPAT", "Square for BPAT", {"type": "Polygon", "coordinates": square(-123, 43, -115, 48)}),
    # a shape whose code is no node of the network: listed, not drawn
    feature("ZZZZ", "Square with a code the network does not have", {"type": "Polygon", "coordinates": square(-110, 40, -108, 42)}),
    # a shape with a node's name and no code: never matched by its name
    feature("", "ISO New England", {"type": "Polygon", "coordinates": square(-73, 42, -70, 45)}),
]

if __name__ == "__main__":
    out = os.path.join(HERE, "squares.geojson")
    with open(out, "w", encoding="utf-8", newline="\n") as f:
        json.dump({"type": "FeatureCollection", "name": "session180 fixture: made-up squares, not boundaries", "features": FEATURES}, f, indent=1)
        f.write("\n")
    print(out)
