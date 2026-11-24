"""Fit checks on a post's stills (session 9900). Usage: fitcheck.py <spec.json> <stills_dir> [--height 1350]
At each row's highlight peak (frame 64 + 40 i + 16): the active row's label ink ends at least 8 px (2160 scale) left of
its bar, the bar track ends left of the number, the number ends left of the second figure, and no ink lies outside
the 72 px margins. On the last frame: the title's line count and the source line's line count.
Prints one line a check and exits 1 when any fails."""
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

spec = json.load(open(sys.argv[1]))
d = Path(sys.argv[2])
H = spec["height"]
if "--height" in sys.argv:
    H = int(sys.argv[sys.argv.index("--height") + 1])
S = 2
W = 1080 * S
FOG = np.array([0xF7, 0xF3, 0xEA])
CARD = np.array([0x8C, 0x15, 0x15])
TRACK = np.array([0xE3, 0xDE, 0xD1])
CAP = np.array([0x6B, 0x67, 0x5F])
n = len(spec["rows"])
bad = 0


def load(fr):
    p = d / f"{spec['id']}_{W}x{H * S}_f{fr:03d}.png"
    return np.asarray(Image.open(p).convert("RGB"), dtype=np.int16), p.name


def near(img, c, tol=40):
    return np.abs(img - c).sum(axis=2) < tol


def say(ok, msg):
    global bad
    bad += not ok
    print(("PASS " if ok else "FAIL ") + msg)


def runs(xs):
    """contiguous runs of a sorted int array, allowing gaps under 6 px"""
    out = []
    for x in xs:
        if out and x - out[-1][1] < 6:
            out[-1][1] = x
        else:
            out.append([x, x])
    return out


for i in range(n):
    fr = 64 + 40 * i + 16
    img, name = load(fr)
    ink = ~near(img, FOG, 24)
    say(not ink[:, : 72 * S - 2].any() and not ink[:, W - 72 * S + 2:].any(), f"{name} row {i + 1}: no ink outside the side margins")
    card = near(img, CARD, 60)
    ys = np.nonzero(card[: (H - 60) * S].any(axis=1))[0]
    ys = ys[ys > 250 * S]
    if len(ys) == 0:
        say(spec["rows"][i]["value"] == 0, f"{name} row {i + 1}: no cardinal pixels (value {spec['rows'][i]['value']})")
        continue
    y0, y1 = ys.min(), ys.max()
    band = slice(max(0, y0 - 30), min(H * S, y1 + 30))
    trk = near(img[band], TRACK, 30) | near(img[band], CARD, 60)
    # the bar: the longest horizontal run of track or cardinal at the band's middle rows
    mid = trk[trk.shape[0] // 2 - 4: trk.shape[0] // 2 + 4].all(axis=0)
    rr = runs(np.nonzero(mid)[0])
    bar = max(rr, key=lambda r: r[1] - r[0])
    left_ink = np.nonzero(ink[band][:, : bar[0] - 1].any(axis=0))[0]
    label_right = left_ink.max() if len(left_ink) else 0
    say(bar[0] - label_right >= 8, f"{name} row {i + 1}: label ends {bar[0] - label_right} px before the bar")
    cardx = np.nonzero(card[band][:, bar[1] + 2:].any(axis=0))[0] + bar[1] + 2
    if len(cardx):
        say(cardx.min() - bar[1] >= 8, f"{name} row {i + 1}: number starts {cardx.min() - bar[1]} px after the bar track")
        if any("second" in r for r in spec["rows"]):
            capx = np.nonzero(near(img[band], CAP, 40)[:, cardx.max() + 1:].any(axis=0))[0]
            if len(capx):
                say(capx.min() >= 8, f"{name} row {i + 1}: second figure starts {capx.min()} px after the number")

img, name = load(spec["frames"] - 1)
ink = ~near(img, FOG, 24)
say(not ink[:, : 72 * S - 2].any() and not ink[:, W - 72 * S + 2:].any(), f"{name}: no ink outside the side margins")
say(not ink[(H - 40) * S:].any(), f"{name}: nothing in the bottom 40 px")
top = 320 if H > 1080 else 290


def lines(region):
    rows = region.any(axis=1)
    return len(runs(np.nonzero(rows)[0])) if rows.any() else 0


# title: text between y 126 and the first row; source: below the rule
tl = lines(ink[126 * S: (top - 10) * S])
say(1 <= tl <= 2, f"{name}: title in {tl} line(s)")
sl = lines(ink[(H - 196 + 10) * S:])
say(1 <= sl <= 3, f"{name}: source in {sl} line(s)")
print(f"failed={bad}")
sys.exit(1 if bad else 0)
