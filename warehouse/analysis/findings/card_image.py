#!/usr/bin/env python3
"""A finding card as a PNG, drawn by code (session 232).

Energy Research Warehouse (ERW). A card (the scanner's, the watch list's, a finding's) holds everything its picture
needs: the title, the one-line fact (its subtitle), the chart's own points, the callouts and the source line. This
module draws that card with matplotlib in the house style (warehouse/analysis/style.py: the palette, Georgia, the ERW
mark, the source line burned into the bottom), so the weekday Digest can carry it on the site and in the email, and the
weekly hunt can prepare the two LinkedIn sizes. No browser, no model, no number of its own: every figure on the picture
is one the card already holds.

    render(card, path, "digest")             1200 x 880 px, shown at 600 px in the email
    render(card, path, "linkedin_wide")      1200 x 627 px
    render(card, path, "linkedin_square")    1080 x 1080 px

    python warehouse/analysis/findings/card_image.py card.json out.png [size]

Chart kinds drawn: flag_line (a series with its flagged point, its reference lines and its marked span), lines,
line_with_fleet, grouped_bar, stacked_bar_pct, bars_free, scatter, and multiples (its first panel's own chart). A kind
that is not drawn raises ValueError: no picture is better than a wrong one.
"""

import json
import math
import os
import sys
import textwrap

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.abspath(os.path.join(HERE, "..")))
import style  # noqa: E402

# session 815: "phone", 600 by 760, drawn for a 390 px screen (the page serves it under 640 px): the type at 0.8 of the
# digest's point sizes on a canvas half as wide, so a label reads twice as large on a phone as the 1200 px picture scaled
SIZES = {"digest": (1200, 880), "linkedin_wide": (1200, 627), "linkedin_square": (1080, 1080), "phone": (600, 760)}
SCALE = {"digest": 1.0, "linkedin_wide": 0.95, "linkedin_square": 1.15, "phone": 0.8}
CALLOUTS = {"digest": 3, "linkedin_wide": 0, "linkedin_square": 3, "phone": 3}   # the wide size has no room below its chart
NAN = float("nan")
WARNINGS = []      # session 9820: what the last render had to cut (a title past three lines, a source line past four)


def _vals(values):
    return [NAN if v is None else float(v) for v in values]


def _dates(x):
    """The x values as dates when every one is a day (YYYY-MM-DD) or a month (YYYY-MM); else None."""
    import datetime as dt
    out = []
    for v in x:
        s = str(v)
        try:
            out.append(dt.datetime.strptime(s if len(s) == 10 else s + "-01", "%Y-%m-%d"))
        except ValueError:
            return None
    return out or None


def _position(x, pos, wanted):
    """Where a named x value sits on the axis (None when the chart does not hold it)."""
    try:
        return pos[[str(v) for v in x].index(str(wanted))]
    except ValueError:
        return None


def _num(v, nd):
    """A number with the chart's own count of decimals, thousands separated."""
    return f"{float(v):,.{int(nd)}f}"


def _years(x):
    """The x values as years (integers) when every one is a four-digit year; else None (session 9820)."""
    s = [str(v) for v in x]
    return [int(v) for v in s] if s and all(len(v) == 4 and v.isdigit() for v in s) else None


def _broken(pos, vals):
    """The points with a break (NaN) wherever years are missing between two of them, so that the line does not join
    across years the table does not hold (session 9820: a chart drew 2003 and 2012 one step apart)."""
    xs, ys = [], []
    for i, (p, v) in enumerate(zip(pos, vals)):
        if i and p - pos[i - 1] > 1:
            xs.append((p + pos[i - 1]) / 2)
            ys.append(NAN)
        xs.append(p)
        ys.append(v)
    return xs, ys


def _year_ticks(ax, years):
    """A labelled tick every few years counted back from the last, so the marked year is always labelled; a short tick
    at every year held."""
    span = years[-1] - years[0]
    step = max(1, math.ceil((span + 1) / 12))
    # the first year labelled too when a step up to twice as long divides the span (1997 to 2025 by fours)
    step = next((s for s in range(step, 2 * step + 1) if span % s == 0), step)
    major = list(range(years[-1], years[0] - 1, -step))[::-1]
    ax.set_xticks(major)
    ax.set_xticklabels([str(y) for y in major])
    ax.set_xticks([y for y in years if y not in major], minor=True)
    ax.tick_params(axis="x", which="minor", length=3.5)


def _flag_line(ax, ch, pt, sans):
    x = ch["x"]
    nd = ch.get("decimals", 2)
    dates = _dates(x)
    years = None if dates else _years(x)
    pos = dates if dates else (years or list(range(len(x))))
    gaps = bool(years) and any(b - a > 1 for a, b in zip(years, years[1:]))
    labels = []                                         # session 9820: placed after the axes are drawn, clear of the lines
    for i, s in enumerate(ch["series"]):
        xs, ys = _broken(pos, _vals(s["values"])) if gaps else (pos, _vals(s["values"]))
        color = style.BLUE if i else style.INK
        ax.plot(xs, ys, color=color, lw=1.7 if i else 1.9, ls="--" if i else "-",   # session 267: the comparison in blue, cardinal kept for the flag
                marker="o" if gaps else None, ms=3.5, label=s["name"], zorder=3)
        if len(ch["series"]) > 1:                       # brand, section 6: a series is named on the chart, in its own color; no legend
            labels.append({"kind": "series", "text": s["name"], "color": color, "size": pt(10), "points": list(zip(pos, _vals(s["values"])))})
    for r in ch.get("ref_lines") or []:
        ax.axhline(r["value"], color=style.MUTED, lw=1.0, ls=(0, (5, 3)), zorder=2)
        labels.append({"kind": "ref", "text": f"{r['name']}: {_num(r['value'], nd)}", "y": r["value"], "color": style.MUTED, "size": pt(9.5)})
    area = ch.get("mark_area")
    if area:
        if dates:                                       # a span's ends are days: they need not be points of the series
            ends = _dates([area["from"], area["to"]])
            a, b = (max(ends[0], dates[0]), min(ends[1], dates[-1])) if ends else (None, None)
        else:
            a, b = _position(x, pos, area["from"]), _position(x, pos, area["to"])
        if a is not None and b is not None:
            ax.axvspan(a, b, color=style.ACCENT, alpha=0.13, lw=0, zorder=1)
            ax.annotate(area.get("label", ""), xy=(b, 1.0), xycoords=("data", "axes fraction"), xytext=(-2, -4), textcoords="offset points",
                        va="top", ha="right", fontsize=pt(9.5), color=style.ACCENT, family=sans)
    m = ch.get("mark")
    if m:
        p = _position(x, pos, m["x"])
        if p is not None and m.get("value") is not None:
            ax.scatter([p], [m["value"]], s=110, color=style.ACCENT, edgecolor=style.PAPER, linewidth=1.5, zorder=6)
            labels.insert(0, {"kind": "mark", "text": f"{_num(m['value'], nd)} ({m['x']})", "xy": (p, m["value"]), "color": style.ACCENT,
                              "size": pt(11), "weight": "bold"})
    if dates:
        import matplotlib.dates as mdates
        span = (dates[-1] - dates[0]).days if len(dates) > 1 else 0
        if span < 150 and len(dates) <= 150:            # session 9820: every k-th day counted back from the last (the locator put Jan 31 beside Feb 01)
            from matplotlib.ticker import FuncFormatter
            k = max(1, math.ceil(len(dates) / 8))
            ax.set_xticks(dates[::-1][::k][::-1])
            ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: f"{mdates.num2date(v):%b} {mdates.num2date(v).day}"))
        else:
            ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=4, maxticks=8))
            ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y" if span < 2200 else "%Y"))
    elif years:
        _year_ticks(ax, years)                          # session 9820: years at their own places, gaps shown as gaps
    else:
        _category_ticks(ax, [str(v) for v in x])        # any other names: the points sit at 0, 1, 2 ...
    ax._erw_labels = labels
    return False                                        # no legend: each series is named on its line


def _segments_hit(rect, pts):
    """Whether a polyline (display points, NaN for a break) crosses the rectangle (x0, y0, x1, y1): Liang and Barsky."""
    x0, y0, x1, y1 = rect
    for (ax_, ay), (bx, by) in zip(pts, pts[1:]):
        if any(math.isnan(v) for v in (ax_, ay, bx, by)):
            continue
        dx, dy, t0, t1, ok = bx - ax_, by - ay, 0.0, 1.0, True
        for p, q in ((-dx, ax_ - x0), (dx, x1 - ax_), (-dy, ay - y0), (dy, y1 - ay)):
            if p == 0:
                if q < 0:
                    ok = False
                    break
            else:
                t = q / p
                if p < 0:
                    t0 = max(t0, t)
                else:
                    t1 = min(t1, t)
                if t0 > t1:
                    ok = False
                    break
        if ok:
            return True
    for (px_, py_) in pts:                              # a lone point between two breaks
        if not (math.isnan(px_) or math.isnan(py_)) and x0 <= px_ <= x1 and y0 <= py_ <= y1:
            return True
    return False


def _place_labels(fig, ax, labels, sans):
    """Session 9820: each label of a flag_line where it crosses no line, no point and no other label. The marked figure
    first, then the reference lines', then the series' names. Every candidate place is tried in order; the first clear
    one is kept, else the one that crosses least. Before, the reference label sat where the line starts and the marked
    figure on the line that comes down to it."""
    if not labels:
        return
    r = fig.canvas.get_renderer()
    box = ax.get_window_extent(r)
    allowed = (box.x0 - 2, box.y0 + 2, box.x1 + 20, box.y1 + 10)
    lines = []
    for ln in ax.get_lines():
        xd, yd = ln.get_xdata(), ln.get_ydata()
        try:
            xd = [float(v) for v in ax.convert_xunits(xd)]
        except (TypeError, ValueError):
            continue
        tr = ln.get_transform()
        lines.append([tuple(tr.transform((a, b))) if not (math.isnan(a) or math.isnan(float(b))) else (NAN, NAN) for a, b in zip(xd, yd)])
    lo, hi = ax.get_ylim()
    dots = []
    for coll in ax.collections:
        for off in coll.get_offsets():
            dots.append(tuple(ax.transData.transform((float(off[0]), float(off[1])))))
    placed = []

    def cost(bb, skip_y=None):
        rect = (bb.x0 - 5, bb.y0 - 5, bb.x1 + 5, bb.y1 + 5)          # five pixels clear of any line
        if rect[0] < allowed[0] or rect[1] < allowed[1] or rect[2] > allowed[2] or rect[3] > allowed[3]:
            return 1000
        c = sum(3 for pts in lines if _segments_hit(rect, pts) and not (skip_y is not None and all(abs(p[1] - skip_y) < 3 for p in pts if not math.isnan(p[1]))))
        c += sum(3 for (dx, dy) in dots if rect[0] - 7 <= dx <= rect[2] + 7 and rect[1] - 7 <= dy <= rect[3] + 7)
        c += sum(5 for p in placed if not (rect[2] < p.x0 or rect[0] > p.x1 or rect[3] < p.y0 or rect[1] > p.y1))
        return c

    def best(make, candidates, skip_y=None):
        chosen, low = None, None
        for cand in candidates:
            t = make(cand)
            bb = t.get_window_extent(r)
            c = cost(bb, skip_y)
            if low is None or c < low:
                if chosen is not None:
                    chosen.remove()
                chosen, low = t, c
            else:
                t.remove()
            if c == 0:
                break
        placed.append(chosen.get_window_extent(r))
        if low:
            WARNINGS.append(f"no clear place for the label {chosen.get_text()!r} (cost {low})")
        return chosen

    for lab in labels:
        kw = dict(fontsize=lab["size"], color=lab["color"], family=sans, fontweight=lab.get("weight", "normal"), zorder=7)
        if lab["kind"] == "mark":
            spots = [(-12, 12, "right", "bottom"), (-12, -12, "right", "top"), (-14, 0, "right", "center"), (0, 14, "center", "bottom"),
                     (0, -14, "center", "top"), (-12, 26, "right", "bottom"), (-12, -26, "right", "top"), (-34, 12, "right", "bottom"),
                     (-34, -12, "right", "top"), (0, 28, "center", "bottom"), (0, -28, "center", "top"), (-12, 42, "right", "bottom"),
                     (-12, -42, "right", "top"), (0, 42, "center", "bottom"), (0, -42, "center", "top"), (-60, 0, "right", "center"),
                     (-12, 60, "right", "bottom"), (-12, -60, "right", "top"), (0, -60, "center", "top"), (12, 12, "left", "bottom"),
                     (12, -12, "left", "top")]
            best(lambda s, lab=lab, kw=kw: ax.annotate(lab["text"], xy=lab["xy"], xytext=(s[0], s[1]), textcoords="offset points", ha=s[2], va=s[3],
                                                         bbox=dict(facecolor=style.PAPER, edgecolor="none", alpha=0.85, pad=1.5), **kw), spots)
        elif lab["kind"] == "ref":
            spots = [(f, side) for f in ((0.006, "left"), (0.994, "right"), (0.25, "center"), (0.5, "center"), (0.75, "center"), (0.12, "left"), (0.88, "right"))
                     for side in (1, -1)]
            yline = ax.transData.transform((0, lab["y"]))[1]
            best(lambda s, lab=lab, kw=kw: ax.annotate(lab["text"], xy=(s[0][0], lab["y"]), xycoords=("axes fraction", "data"), xytext=(0, 3 * s[1]),
                                                         textcoords="offset points", ha=s[0][1], va="bottom" if s[1] > 0 else "top", **kw), spots, skip_y=yline)
        else:
            pts = [p for p in lab["points"] if not math.isnan(p[1])]
            spots = []
            for k, (px_, py_) in enumerate(reversed(pts)):
                ha = "right" if k == 0 else "center"
                spots += [(px_, py_, 9, ha, "bottom"), (px_, py_, -9, ha, "top")]
            best(lambda s, lab=lab, kw=kw: ax.annotate(lab["text"], xy=(s[0], s[1]), xytext=(0, s[2]), textcoords="offset points", ha=s[3], va=s[4], **kw), spots)


def _lines(ax, ch, pt, sans):
    x = [str(v) for v in ch["x"]]
    pos = list(range(len(x)))
    colors = style.series_colors(len(ch["series"]))   # session 267: the brand's series colors
    for i, s in enumerate(ch["series"]):
        ax.plot(pos, _vals(s["values"]), color=s.get("color") or colors[i], lw=2.0, label=s["name"],
                marker="o" if len(x) <= 30 else None, ms=4, zorder=3)
    _category_ticks(ax, x)
    return len(ch["series"]) > 1


def _category_ticks(ax, x):
    step = max(1, math.ceil(len(x) / 12))
    ax.set_xticks(range(len(x)))
    # session 9820: counted back from the last point, so the last (the marked one, on a findings chart) is labelled
    ax.set_xticklabels([v if (len(x) - 1 - k) % step == 0 else "" for k, v in enumerate(x)], rotation=0 if max((len(v) for v in x), default=0) <= 7 else 30,
                       ha="center" if max((len(v) for v in x), default=0) <= 7 else "right")


def _bars(ax, ch, pt, sans, stacked=False):
    x = [str(v) for v in ch["x"]]
    pos = list(range(len(x)))
    series = [s for s in ch["series"] if s.get("type", "bar") != "line"]
    n = max(1, len(series))
    base = [0.0] * len(x)
    colors = style.series_colors(len(series))   # session 267: the brand's series colors
    for i, s in enumerate(series):
        vals = _vals(s["values"])
        color = s.get("color") or colors[i]
        if stacked:
            ax.bar(pos, vals, bottom=base, width=0.72, color=color, label=s["name"], zorder=3)
            base = [b + (0 if math.isnan(v) else v) for b, v in zip(base, vals)]
        else:
            wd = 0.8 / n
            ax.bar([p - 0.4 + wd * (i + 0.5) for p in pos], vals, width=wd, color=color, label=s["name"], zorder=3)
    for j, s in enumerate(s for s in ch["series"] if s.get("type") == "line"):
        ax.plot(pos, _vals(s["values"]), color=style.INK, lw=1.8, marker="o", ms=4, label=s["name"], zorder=4)
    _category_ticks(ax, x)
    return len(ch["series"]) > 1


def _scatter(ax, ch, pt, sans):
    pts = ch.get("points")
    if pts:
        ax.scatter([p[0] for p in pts], [p[1] for p in pts], s=16, color=style.BLUE, alpha=0.55, lw=0, zorder=3)   # session 267: points in blue, the fitted line in cardinal
    for i, s in enumerate(ch.get("series") or []):
        if s.get("points"):
            ax.scatter([p[0] for p in s["points"]], [p[1] for p in s["points"]], s=16, color=[style.BLUE, style.GREY, style.LIGHT, style.INK][i % 4],
                       alpha=0.55, lw=0, label=s.get("name"), zorder=3)
        elif s.get("type") == "line" and s.get("xy"):
            ax.plot([p[0] for p in s["xy"]], [p[1] for p in s["xy"]], color=style.ACCENT, lw=2.0, label=s.get("name"), zorder=4)
    for ln in ch.get("lines") or []:
        if ln.get("xy"):
            ax.plot([p[0] for p in ln["xy"]], [p[1] for p in ln["xy"]], color=style.ACCENT, lw=2.0, label=ln.get("name"), zorder=4)
    return any(s.get("name") for s in (ch.get("series") or []))


def _fleet(ax, ch, pt, sans):
    """A line (or lines) on the left axis and the fleet's size as a shaded step on the right."""
    x = [str(v) for v in ch["x"]]
    dates = _dates(x)
    pos = dates if dates else list(range(len(x)))
    left = [s for s in ch["series"] if not (s.get("y2") or s.get("axis") == "right" or s.get("type") in ("area", "bar"))]
    right = [s for s in ch["series"] if s not in left]
    colors = style.series_colors(len(left))   # session 267: the brand's series colors
    for i, s in enumerate(left):
        ax.plot(pos, _vals(s["values"]), color=s.get("color") or colors[i], lw=1.9, label=s["name"], zorder=3)
    if right:
        ax2 = ax.twinx()
        for s in right:
            ax2.fill_between(pos, _vals(s["values"]), color=style.LIGHT, alpha=0.35, lw=0, label=s["name"], step="mid", zorder=1)
        ax2.set_ylabel(ch.get("y_right_label", ""), color=style.MUTED, fontsize=pt(10), family=sans)
        ax2.tick_params(colors=style.MUTED, labelsize=pt(10))
        for side in ("top", "left", "bottom"):
            ax2.spines[side].set_visible(False)
        ax2.spines["right"].set_color(style.RULE)
        ax.set_zorder(ax2.get_zorder() + 1)
        ax.patch.set_visible(False)
    if dates:
        import matplotlib.dates as mdates
        ax.xaxis.set_major_locator(mdates.AutoDateLocator(minticks=4, maxticks=8))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
    else:
        _category_ticks(ax, x)
    return len(ch["series"]) > 1


def _draw(ax, ch, pt, sans):
    kind = ch.get("kind")
    if kind == "multiples":                             # the first panel's own chart: one grid, as the card's default view
        panels = ch.get("panels") or ch.get("charts") or []
        first = panels[0] if panels else None
        if isinstance(first, dict) and isinstance(first.get("chart"), dict):
            first = first["chart"]
        if not isinstance(first, dict) or first.get("kind") in (None, "multiples"):
            raise ValueError("no drawing for this multiples chart: it holds no panel with a chart of its own")
        return _draw(ax, first, pt, sans), first
    if kind == "flag_line":
        return _flag_line(ax, ch, pt, sans), ch
    if kind == "lines":
        return _lines(ax, ch, pt, sans), ch
    if kind == "line_with_fleet":
        return _fleet(ax, ch, pt, sans), ch
    if kind in ("grouped_bar", "bars_free"):
        return _bars(ax, ch, pt, sans), ch
    if kind == "stacked_bar_pct":
        return _bars(ax, ch, pt, sans, stacked=True), ch
    if kind == "scatter":
        return _scatter(ax, ch, pt, sans), ch
    raise ValueError(f"no drawing for chart kind {kind!r}")


def render(card, path, size="digest", fact=None, kicker=None):
    """Draw the card to `path` (PNG). fact: the one line under the title (default the card's subtitle). kicker: a short
    line above the title (default none). Returns the path. Raises ValueError for a chart it cannot draw."""
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    from matplotlib import font_manager
    from matplotlib.patches import Rectangle
    from matplotlib.ticker import FuncFormatter
    w, h = SIZES[size]
    scale, dpi = SCALE[size], 100
    have = {f.name for f in font_manager.fontManager.ttflist}
    serif = next((f for f in style.SERIF if f in have), "serif")
    sans = next((f for f in style.SANS if f in have), "sans-serif")
    pt = lambda p: p * scale            # noqa: E731  a point size at this picture's scale
    px = lambda p: pt(p) * dpi / 72     # noqa: E731  and its height in pixels
    fig = plt.figure(figsize=(w / dpi, h / dpi), dpi=dpi, facecolor=style.PAPER)
    left, right = 0.045 * w, 0.045 * w
    mark = 52 * scale

    del WARNINGS[:]

    def wrapped(text, size_pt, width_px, family, weight, chars):
        """Session 9820: the lines as wrapped, each measured as drawn and wrapped shorter until every one fits its
        width (the letter widths were guessed before, and a line could run into the mark or off the picture)."""
        lines = textwrap.wrap(str(text), chars)
        rnd = fig.canvas.get_renderer()
        while chars > 12:
            widest = 0.0
            for ln in lines:
                t = fig.text(0, 0, ln, family=family, fontsize=pt(size_pt), fontweight=weight)
                widest = max(widest, t.get_window_extent(rnd).width)
                t.remove()
            if widest <= width_px:
                break
            chars -= 1
            lines = textwrap.wrap(str(text), chars)
        return lines

    def block(text, size_pt, width_px, family, color, y, lh=1.24, weight="normal", max_lines=None, wide=None):
        """Wrapped text from y (pixels from the top) down; returns the y below it. wide: a letter's mean width in ems
        (bold capitals are wider than running text)."""
        chars = max(18, int(width_px / (px(size_pt) * (wide or (0.50 if family == serif else 0.53)))))
        lines = wrapped(text, size_pt, width_px, family, weight, chars)
        if max_lines and len(lines) > max_lines:
            WARNINGS.append(f"cut to {max_lines} lines: {str(text)[:70]}")
            lines = lines[:max_lines]
            lines[-1] = lines[-1].rstrip(" ,;:") + " ..."
        for ln in lines:
            fig.text(left / w, 1 - y / h, ln, family=family, fontsize=pt(size_pt), color=color, va="top", ha="left", fontweight=weight)
            y += px(size_pt) * lh
        return y

    y = 0.04 * h
    if kicker:
        y = block(kicker, 10.5, w - left - right - mark - 80, sans, style.MUTED, y) + 2
    y = block(card["title"], 22, w - left - right - mark - 120 * scale, serif, style.INK, y, 1.18, "bold", 3, wide=0.70)   # session 267: cardinal is not a title's color (docs/brand.md, section 2)
    y = block(fact or card.get("subtitle", ""), 13.5, w - left - right - (mark + 120 * scale if y < 0.04 * h + mark else 0), serif, style.INK, y + 5, 1.3, max_lines=4)
    style._mark(fig, 1 - right / w, 1 - 0.04, mark / h)

    # from the bottom up: the source line, then the callouts
    source = card.get("source_line", "")
    src_chars = max(40, int((w - left - right) / (px(9.5) * 0.53)))
    src = wrapped(source, 9.5, w - left - right, sans, "normal", src_chars)
    if len(src) > 4:                                    # session 9820: four lines, and a longer source line is said, not cut silently
        WARNINGS.append(f"source line cut to 4 lines: {source[:70]}")
    src = src[:4]
    yb = 0.03 * h
    for ln in reversed(src):
        fig.text(left / w, yb / h, ln, family=sans, fontsize=pt(9.5), color=style.MUTED, va="bottom", ha="left")
        yb += px(9.5) * 1.3
    calls = (card.get("callouts") or [])[:CALLOUTS[size]]
    if calls:
        gap = 14 * scale
        bw = (w - left - right - gap * (len(calls) - 1)) / len(calls)
        bh = px(9.5) * 1.35 + px(10.5) * 1.35 * 2 + px(13) * 1.3 + 22 * scale
        yb += 10 * scale
        for k, c in enumerate(calls):
            x0 = left + k * (bw + gap)
            fig.patches.append(Rectangle((x0 / w, yb / h), bw / w, bh / h, transform=fig.transFigure, facecolor=style.PANEL,
                                         edgecolor=style.RULE, linewidth=1.0, zorder=1))
            chars = max(14, int((bw - 24 * scale) / (px(10.5) * 0.53)))
            ty = yb + bh - 10 * scale

            def put(text, size_pt, color, weight="normal", ty=None, x0=x0, chars=chars):
                fig.text((x0 + 12 * scale) / w, ty / h, textwrap.shorten(str(text), int(chars * 10.5 / size_pt), placeholder=" ..."), family=sans,
                         fontsize=pt(size_pt), color=color, va="top", ha="left", fontweight=weight, zorder=2)
            put(c["label"].upper(), 9.5, style.MUTED, ty=ty)
            ty -= px(9.5) * 1.5
            put(f"{c['before']['text']}  ({c['before']['period']})", 10.5, style.MUTED, ty=ty)
            ty -= px(10.5) * 1.45
            put(str(c["after"]["text"]), 13, style.INK, "bold", ty=ty)
            ty -= px(13) * 1.35
            put(f"({c['after']['period']})", 10.5, style.MUTED, ty=ty)
        yb += bh
    ch = card["chart"]
    x_label = ch.get("x_label", "")
    bottom = yb + (58 if x_label else 40) * scale
    top = y + 16 * scale
    # session 815: on the phone canvas (600 px) the axis labels need a wider left margin (a seven-digit label was clipped)
    left_frac = 0.095 if size != "phone" else 0.165
    ax = fig.add_axes([left_frac, bottom / h, (0.86 if ch.get("kind") != "line_with_fleet" else 0.80) - (left_frac - 0.095), max(0.12, 1 - (top + bottom) / h)])
    ax.set_facecolor(style.PAPER)
    legend, drawn = _draw(ax, ch, pt, sans)
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(style.RULE)
    ax.tick_params(which="both", colors=style.MUTED, labelsize=pt(10))
    ax.grid(axis="y", color=style.RULE, lw=0.8, zorder=0)
    ax.set_axisbelow(True)
    ax.yaxis.set_major_formatter(FuncFormatter(lambda v, _: style.fmt(round(v, 2))))
    ax.set_ylabel(drawn.get("y_left_label") or drawn.get("y_label") or "", color=style.MUTED, fontsize=pt(10), family=sans)
    if x_label:
        ax.set_xlabel(textwrap.shorten(x_label, 120, placeholder=" ..."), color=style.MUTED, fontsize=pt(9.5), family=sans)
    lo, hi = ax.get_ylim()
    ax.set_ylim(lo, hi)                                 # session 9820: the scale fixed before the zero line and the labels
    if lo < 0 < hi:
        ax.axhline(0, color=style.INK, lw=0.9, zorder=2.5)   # docs/brand.md, section 6: the zero line is ink
    if getattr(ax, "_erw_labels", None):
        _place_labels(fig, ax, ax._erw_labels, sans)
    if legend:
        ax.legend(loc="upper left", frameon=False, fontsize=pt(9.5), labelcolor=style.MUTED, ncol=1 if len(drawn["series"]) <= 3 else 2)
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    fig.savefig(path, dpi=dpi, facecolor=style.PAPER)
    plt.close(fig)
    return path


if __name__ == "__main__":
    if len(sys.argv) < 3:
        sys.exit("card_image.py card.json out.png [digest|linkedin_wide|linkedin_square]")
    with open(sys.argv[1], encoding="utf-8") as f:
        c = json.load(f)
    c = c.get("card", c) if isinstance(c, dict) else c[0]["card"]
    print(render(c, sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else "digest"))
