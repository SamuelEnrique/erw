"""Compare every PNG in two folders pixel by pixel. Session 9900. Usage: pixcmp.py <before_dir> <after_dir>"""
import sys
from pathlib import Path

import numpy as np
from PIL import Image

a, b = Path(sys.argv[1]), Path(sys.argv[2])
bad = 0
for fa in sorted(a.glob("*.png")):
    fb = b / fa.name
    if not fb.exists():
        print(f"MISSING {fa.name}")
        bad += 1
        continue
    x = np.asarray(Image.open(fa).convert("RGBA"), dtype=np.int16)
    y = np.asarray(Image.open(fb).convert("RGBA"), dtype=np.int16)
    if x.shape != y.shape:
        print(f"SIZE {fa.name} {x.shape} {y.shape}")
        bad += 1
        continue
    d = np.abs(x - y).max(axis=2)
    n = int((d > 0).sum())
    print(f"{'SAME' if n == 0 else 'DIFF'} {fa.name} {x.shape[1]}x{x.shape[0]} differing_pixels={n} max_channel_diff={int(d.max())}")
    bad += n > 0
print(f"files_differing={bad}")
sys.exit(1 if bad else 0)
