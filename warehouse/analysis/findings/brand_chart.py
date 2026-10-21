#!/usr/bin/env python3
"""A finding's picture in the ERW brand (docs/brand.md), drawn by matplotlib (the hunt of 20 October 2026).

Energy Research Warehouse (ERW). Two sizes: square (1200 by 1200, LinkedIn's feed) and wide (1600 by 900, the Roundup's
chart of the week). The page is white; the type is Source Serif 4 at weight 600 for the headline, IBM Plex Sans for
every label and axis, IBM Plex Mono for the figures in the fog panel; cardinal is the one accent (the record period's
bar, the two marked points of a trend); grid lines are the rule color, horizontal only; the zero line is ink; no frame
around the plot; the source line is burned into the bottom; the ERW mark (the E in the cardinal square, with ERW beside
it in the serif) sits at the top right. An incomplete period is hatched and named. Nothing here computes a number: every
figure drawn is one the finding's record holds.

The fonts are the static instances in warehouse/analysis/fonts/ (built from the Open Font License files of Google Fonts
with fontTools; the OFL texts are beside them). A font that is not there falls back to the machine's serif or sans, and
the picture says nothing about it: render() returns the fallback used in its second value.

    render(record, path, "square" | "wide")      -> (path, {"serif": ..., "sans": ..., "mono": ...})
    python warehouse/analysis/findings/brand_chart.py finding.json out.png [square|wide]
"""

import datetime as dt
import json
import math
import os
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
FONTS = os.path.join(HERE, "..", "fonts")
SIZES = {"square": (1200, 1200), "wide": (1600, 900)}
# docs/brand.md, section 2
PAGE, FOG, RULE, CAPTIONS, INK, CARDINAL, BLUE, LIGHT = "#FFFFFF", "#F7F3EA", "#E3DED1", "#6B675F", "#2E2D29", "#8C1515", "#3C6E9E", "#8F8A80"
FONT_FILES = {"serif600": "SourceSerif4-Semibold.ttf", "serif400": "SourceSerif4-Regular.ttf", "sans400": "IBMPlexSans-Regular.ttf",
              "sans500": "IBMPlexSans-Medium.ttf", "sans600": "IBMPlexSans-SemiBold.ttf", "mono400": "IBMPlexMono-Regular.ttf", "mono500": "IBMPlexMono-Medium.ttf"}


def fonts():
    """FontProperties for each role, from the brand's files where they are there, else the machine's fallbacks."""
    from matplotlib import font_manager
    out, used = {}, {}
    have = {f.name for f in font_manager.fontManager.ttflist}
    fallback = {"serif": next((f for f in ("Georgia", "Times New Roman", "DejaVu Serif") if f in have), "serif"),
                "sans": next((f for f in ("Segoe UI", "Helvetica", "Arial", "DejaVu Sans") if f in have), "sans-serif"),
                "mono": next((f for f in ("Consolas", "DejaVu Sans Mono", "Courier New") if f in have), "monospace")}
    for role, name in FONT_FILES.items():
        path = os.path.join(FONTS, name)
        kind = role[:-3] if not role.startswith("serif") else "serif"
        if os.path.exists(path):
            out[role] = font_manager.FontProperties(fname=path)
            used[kind] = used.get(kind, name.split("-")[0].replace("SourceSerif4", "Source Serif 4").replace("IBMPlexSans", "IBM Plex Sans").replace("IBMPlexMono", "IBM Plex Mono"))
        else:
            fam = fallback[kind]
            out[role] = font_manager.FontProperties(family=fam, weight="bold" if role.endswith("600") else ("medium" if role.endswith("500") else "normal"))
            used[kind] = fam
    return out, used


def num(v, nd):
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return "not held"
    return f"{v:,.{int(nd)}f}"


def period_label(p, grain):
    if grain == "month":
        return dt.date(int(str(p)[:4]), int(str(p)[5:7]), 1).strftime("%b %Y")
    return str(p)


def mark(fig, x, y, h, serif):
    """The ERW mark at figure coordinates (x, y) = its top right corner, h its height in figure units: the cardinal
    square with the white stem and three bars (docs/brand/erw-mark.svg: 14, 11 and 17 of 32 units), ERW in the serif,
    ink, to its left (docs/brand.md, section 8: the wordmark sets ERW in Source Serif 4 at 600 beside the square)."""
    from matplotlib.patches import FancyBboxPatch, Rectangle
    w_px, h_px = fig.get_size_inches() * fig.dpi
    w = h * h_px / w_px
    u, v = w / 32, h / 32
    fig.patches.append(FancyBboxPatch((x - w, y - h), w, h, boxstyle=f"round,pad=0,rounding_size={3 * v}", transform=fig.transFigure,
                                      color=CARDINAL, zorder=5, mutation_aspect=w_px / h_px))
    for rx, ry, rw, rh in ((8, 7, 3, 18), (8, 7, 14, 3), (8, 14, 11, 3), (8, 22, 17, 3)):
        fig.patches.append(Rectangle((x - w + rx * u, y - (ry + rh) * v), rw * u, rh * v, transform=fig.transFigure, color=PAGE, zorder=6, linewidth=0))
    size = h * h_px * 0.60 * 72 / fig.dpi
    fig.text(x - w - 0.008, y - h / 2, "ERW", ha="right", va="center", color=INK, fontproperties=serif, fontsize=size)


def headline_words(r):
    """The serif headline: what the data found, in one line or two."""
    c, g, nd, unit = r["claim"], r["grain"], r["decimals"], r["unit"]
    if c["kind"] == "record":
        what = "highest" if c["direction"] == "high" else "lowest"
        return f"{num(c['value'], nd)} {unit} in {period_label(c['period'], g)}, the {what} of the {len(c['periods'])} complete {g}s held"
    return f"{num(c['last'], nd)} {unit} in {period_label(c['last_year'], g)}, {c['direction']} from {num(c['first'], nd)} in {period_label(c['first_year'], g)}"


def render(record, path, size="wide"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib.patches import Rectangle
    from matplotlib.ticker import FuncFormatter
    F, used = fonts()
    w, h = SIZES[size]
    dpi = 100
    fig = plt.figure(figsize=(w / dpi, h / dpi), dpi=dpi, facecolor=PAGE)
    px = lambda pt: pt * dpi / 72  # noqa: E731
    gutter = 64 if size == "wide" else 56
    left = gutter / w
    r = record
    c, g, nd, unit = r["claim"], r["grain"], r["decimals"], r["unit"]
    serif_pt, sub_pt, kicker_pt, body_pt, cap_pt = (34, 17, 13, 14, 12) if size == "wide" else (36, 18, 13, 14, 12)

    def block(text, fp, pt, width_px, color, y, lh=1.25, max_lines=None):
        chars = max(20, int(width_px / (px(pt) * 0.50)))
        lines = textwrap.wrap(text, chars)
        if max_lines and len(lines) > max_lines:
            lines = lines[:max_lines]
            lines[-1] = lines[-1].rstrip(" ,;:") + " ..."
        for ln in lines:
            fig.text(left, 1 - y / h, ln, fontproperties=fp, fontsize=pt, color=color, va="top", ha="left")
            y += px(pt) * lh
        return y

    # the kicker, the headline, the subtitle; the mark at the top right
    y = 44 if size == "wide" else 48
    mark_h = 44
    y = block(f"{r['region_words']}  ·  {r['title'].capitalize()}", F["sans500"], kicker_pt, w - 2 * gutter - 200, CAPTIONS, y, 1.3, 1) + 6
    y = block(headline_words(r), F["serif600"], serif_pt, w - 2 * gutter - 160, INK, y, 1.18, 3) + 8
    y = block(r["label"][0].upper() + r["label"][1:], F["sans400"], sub_pt, min(w - 2 * gutter, 68 * px(sub_pt) * 0.5), CAPTIONS, y, 1.4, 3)
    mark(fig, 1 - gutter / w, 1 - 40 / h, mark_h / h, F["serif600"])

    # from the bottom up: the source line, then the fog panel with the figures
    src_lines = textwrap.wrap(r["source_line"], max(60, int((w - 2 * gutter) / (px(cap_pt) * 0.50))))[:3]
    yb = 36
    for ln in reversed(src_lines):
        fig.text(left, yb / h, ln, fontproperties=F["sans400"], fontsize=cap_pt, color=CAPTIONS, va="bottom", ha="left")
        yb += px(cap_pt) * 1.45
    yb += 14
    if c["kind"] == "record":
        cells = [(f"{period_label(c['period'], g)}, the record {'high' if c['direction'] == 'high' else 'low'}", num(c["value"], nd), unit),
                 (f"{period_label(c['previous_period'], g)}, the previous {'high' if c['direction'] == 'high' else 'low'}", num(c["previous"], nd), unit),
                 ("The margin", f"{'+' if c['direction'] == 'high' else '-'}{num(c['margin_pct'], 1)}", "percent")]
    else:
        cells = [(period_label(c["first_year"], g), num(c["first"], nd), unit), (period_label(c["last_year"], g), num(c["last"], nd), unit),
                 ("The change", f"{'+' if c['change'] > 0 else '-'}{num(abs(c['change']), nd)}", unit)]
    panel_h = 92 if size == "wide" else 100
    gap = 16
    cw = (w - 2 * gutter - gap * (len(cells) - 1)) / len(cells)
    for k, (label, fig_, u) in enumerate(cells):
        x0 = gutter + k * (cw + gap)
        fig.patches.append(Rectangle((x0 / w, yb / h), cw / w, panel_h / h, transform=fig.transFigure, facecolor=FOG, edgecolor=RULE, linewidth=1.0, zorder=1))
        fig.text((x0 + 16) / w, (yb + panel_h - 16) / h, textwrap.shorten(label, 44, placeholder=" ..."), fontproperties=F["sans400"], fontsize=cap_pt, color=CAPTIONS, va="top", ha="left", zorder=2)
        fig.text((x0 + 16) / w, (yb + 18) / h, fig_, fontproperties=F["mono500"], fontsize=24 if size == "wide" else 26, color=INK, va="bottom", ha="left", zorder=2)
        fx = (x0 + 16) / w + len(fig_) * px(24 if size == "wide" else 26) * 0.62 / w
        fig.text(fx + 8 / w, (yb + 20) / h, u, fontproperties=F["sans400"], fontsize=cap_pt, color=CAPTIONS, va="bottom", ha="left", zorder=2)
    yb += panel_h + 24

    # the chart
    top = y + 44
    ax = fig.add_axes([left + 0.012, (yb + 34) / h, 1 - 2 * left - 0.02, max(0.15, 1 - (top + yb + 34) / h)])
    ax.set_facecolor(PAGE)
    series = list(r["series"])
    while series and not series[0]["complete"]:          # a history that starts mid-period: the first incomplete periods are not in the window
        series = series[1:]
    periods = [s["period"] for s in series]
    values = [s["value"] for s in series]
    complete = [bool(s["complete"]) for s in series]
    pos = list(range(len(periods)))
    if c["kind"] == "record":
        colors = [CARDINAL if str(p) == str(c["period"]) else (LIGHT if not comp else INK) for p, comp in zip(periods, complete)]
        bars = ax.bar(pos, values, width=0.72, color=colors, zorder=3, linewidth=0)
        for b, comp in zip(bars, complete):
            if not comp:
                b.set_hatch("////")
                b.set_edgecolor(PAGE)
        i = [str(p) for p in periods].index(str(c["period"]))
        ax.annotate(num(c["value"], nd), xy=(i, c["value"]), xytext=(0, 5), textcoords="offset points", ha="center", va="bottom",
                    fontproperties=F["sans600"], fontsize=body_pt, color=CARDINAL, zorder=6)
        j = [str(p) for p in periods].index(str(c["previous_period"]))
        ax.annotate(num(c["previous"], nd), xy=(j, c["previous"]), xytext=(0, 5), textcoords="offset points", ha="center", va="bottom",
                    fontproperties=F["sans500"], fontsize=body_pt, color=INK, zorder=6)
    else:
        full_pos = [i for i, comp in enumerate(complete) if comp]
        ax.plot([pos[i] for i in full_pos], [values[i] for i in full_pos], color=INK, lw=1.5, zorder=3)
        if len(full_pos) <= 40:
            ax.scatter([pos[i] for i in full_pos], [values[i] for i in full_pos], s=18, color=INK, zorder=4)
        open_pos = [i for i, comp in enumerate(complete) if not comp]
        if open_pos:
            ax.scatter([pos[i] for i in open_pos], [values[i] for i in open_pos], s=26, facecolors=PAGE, edgecolors=LIGHT, linewidths=1.2, zorder=4)
            for i in open_pos:
                ax.annotate(f"{period_label(periods[i], g)}: {series[i]['n']:,} held, not complete", xy=(pos[i], values[i]), xytext=(-6, -14),
                            textcoords="offset points", ha="right", va="top", fontproperties=F["sans400"], fontsize=cap_pt, color=CAPTIONS)
        for key, val_, dy in ((c["first_year"], c["first"], 10), (c["last_year"], c["last"], 10)):
            i = [str(p) for p in periods].index(str(key))
            ax.scatter([pos[i]], [val_], s=70, color=CARDINAL, edgecolor=PAGE, linewidth=1.5, zorder=6)
            ax.annotate(f"{num(val_, nd)} ({period_label(key, g)})", xy=(pos[i], val_), xytext=(0, dy), textcoords="offset points", ha="center", va="bottom",
                        fontproperties=F["sans600"], fontsize=body_pt, color=CARDINAL, zorder=7,
                        bbox=dict(facecolor=PAGE, edgecolor="none", alpha=0.9, pad=1.5))
    step = max(1, math.ceil(len(periods) / (14 if size == "wide" else 10)))
    ax.set_xticks(pos)
    ax.set_xticklabels([period_label(p, g) if k % step == 0 else "" for k, p in enumerate(periods)], fontproperties=F["sans400"], fontsize=cap_pt, color=CAPTIONS)
    ax.tick_params(axis="x", colors=CAPTIONS, length=0, pad=6)
    ax.tick_params(axis="y", colors=CAPTIONS, length=0, pad=4, labelsize=cap_pt)
    for lab in ax.get_yticklabels():
        lab.set_fontproperties(F["sans400"])
        lab.set_fontsize(cap_pt)
        lab.set_color(CAPTIONS)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: (f"{v:,.{min(nd, 2)}f}".rstrip("0").rstrip(".") if abs(v) < 1000 else f"{v:,.0f}") if v else "0"))
    ax.grid(axis="y", color=RULE, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    for side in ("top", "right", "left", "bottom"):
        ax.spines[side].set_visible(False)
    ax.axhline(0, color=INK, lw=1.0, zorder=2)
    ax.text(0.0, 1.02, unit, transform=ax.transAxes, fontproperties=F["sans400"], fontsize=cap_pt, color=CAPTIONS, va="bottom", ha="left")
    lo, hi = min(values + [0]), max(values + [0])
    pad = (hi - lo) * 0.14 or 1
    ax.set_ylim(lo - (pad if lo < 0 else 0), hi + pad)
    ax.set_xlim(-0.6, len(periods) - 0.4)
    if any(not comp for comp in complete):
        ax.text(1.0, 1.02, "A hatched bar or an open point is a period not complete in the table; not part of the claim.", transform=ax.transAxes,
                fontproperties=F["sans400"], fontsize=cap_pt, color=CAPTIONS, va="bottom", ha="right")
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    fig.savefig(path, dpi=dpi, facecolor=PAGE)
    plt.close(fig)
    return path, used


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("brand_chart.py finding.json out.png [square|wide]")
    with open(sys.argv[1], encoding="utf-8") as f:
        rec = json.load(f)
    print(render(rec, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "wide"))
