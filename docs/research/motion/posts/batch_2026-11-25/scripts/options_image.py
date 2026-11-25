"""Session 9901: one comparison image a post, the square final frames of option A and option B side by side, labelled
A and B, into docs/reviews/linkedin/img/batch_2026-11-25/<post>_options.png. Reads the thumbnails the render wrote.
Usage: python options_image.py [<stills_dir>]
With <stills_dir>, a post whose thumbnails are not rendered yet takes the square final-frame stills of batch_9901.mjs
(<stills_dir>/<post>_<a|b>_x_f449.png, the same frame at the same scale)."""
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
BATCH = os.path.dirname(HERE)
REPO = os.path.abspath(os.path.join(BATCH, "..", "..", "..", "..", ".."))
OUT = os.path.join(REPO, "docs", "reviews", "linkedin", "img", "batch_2026-11-25")
POSTS = ["thanksgiving_peak_hour", "thanksgiving_gasoline", "caiso_battery_peak", "canada_new_york_flow", "dominion_mean_hour",
         "ercot_solar_tight_hours", "texas_cold_peak", "uranium_us_origin", "us_share_world_oil"]
os.makedirs(OUT, exist_ok=True)
font = ImageFont.truetype("C:/Windows/Fonts/segoeuib.ttf", 64)
S, PAD, TOP = 1080, 40, 110
for p in POSTS:
    files = [os.path.join(BATCH, p, f"{p}_{o}_x_thumb.png") for o in "ab"]
    if not all(os.path.exists(f) for f in files) and len(sys.argv) > 1:
        files = [os.path.join(sys.argv[1], f"{p}_{o}_x_f449.png") for o in "ab"]
    if not all(os.path.exists(f) for f in files):
        print("missing", p)
        continue
    c = Image.new("RGB", (2 * S + 3 * PAD, S + TOP + PAD), (255, 255, 255))
    d = ImageDraw.Draw(c)
    for k, (f, lab) in enumerate(zip(files, "AB")):
        im = Image.open(f).convert("RGB").resize((S, S), Image.LANCZOS)
        x = PAD + k * (S + PAD)
        c.paste(im, (x, TOP))
        d.rectangle([x - 2, TOP - 2, x + S + 1, TOP + S + 1], outline=(180, 175, 165), width=2)
        d.text((x, 22), f"Option {lab}", font=font, fill=(46, 45, 41))
    c.save(os.path.join(OUT, f"{p}_options.png"))
    print("written", p)
