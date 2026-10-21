"""House style for Automated Analysis (platform tool 26): one chart spec, three sizes.

Energy Research Warehouse (ERW), session 23. Every template's render() builds a chart spec (a plain
dict) and hands it here:

    spec = {"kind": "line" | "bar" | "scatter",
            "title": ..., "subtitle": ..., "source": "the source line",
            "x": [...] (category labels or ISO timestamps; scatter: numbers),
            "x_label": ..., "y_label": ..., "x_time": bool, "stacked": bool,
            "series": [{"name": ..., "values": [...], "y2": bool (optional, a second axis)}],
            "y2_label": ... (optional),
            "mark": {"series": i, "at": j, "label": "28.08 USD/MWh", "key": "week of 2026-09-20 to 2026-09-26"}
                    (optional, session 533: the one value the chart's finding names, series i at x[j], ringed in
                    cardinal and labelled with the figure and its key; templates/common.py headline_mark sets it)}

    echarts(spec)                the site's interactive chart: an ECharts option (JSON), in the site's tokens
    png(spec, path, "email")      1200 x 750 px, shown at 600 px in the email
    png(spec, path, "social_wide")    1200 x 627 px
    png(spec, path, "social_square")  1080 x 1080 px

The look: the brand's chart colors (docs/brand.md, section 2; session 267, the brief of 14 October 2026): up to
five series in ink, cardinal, blue, grey and light grey, in that order, cardinal being the highlight; more than five
take Paul Tol's eight (--chart-series-1 to -8 in site/app/tokens.css, session 268), with cardinal kept for the one
series a chart marks (series_colors). The page is white, a panel fog, rules and captions in the brand's greys. Until
session 267 it was the Stanford palette (cardinal #8C1515 first, then Lagunita, Poppy, Palo Alto, Plum, Bay, Sky).
Titles in Georgia, the ERW mark (the site's icon, a cardinal square with an E, and "ERW") at the top right, and the
source line burned into the bottom of every PNG, so a chart that travels without its page still names its source.
On the site the option's colors are read from the tokens (components/echarts.ts, LITERAL_TOKENS: each value below is
replaced there by the CSS variable that holds it).
"""

import math
import os

# docs/brand.md, section 2: page, ink, cardinal, captions, rule, fog (site/app/tokens.css, the .brand-a block)
PAPER, INK, ACCENT, MUTED, RULE, PANEL = "#FFFFFF", "#2E2D29", "#8C1515", "#6B675F", "#E3DED1", "#F7F3EA"
BLUE, GREY, LIGHT = "#3C6E9E", "#6B675F", "#8F8A80"      # --chart-blue, --chart-grey, --chart-light
BRAND_SERIES = [INK, ACCENT, BLUE, GREY, LIGHT]           # "Chart series", in this order
# "Many series" (session 268): --chart-series-1 to -8, Paul Tol's colorblind-safe set; cardinal is not among them
MANY_SERIES = ["#4477AA", "#66CCEE", "#228833", "#CCBB44", "#EE6677", "#AA3377", "#BBBBBB", "#EEAA44"]
PALETTE = BRAND_SERIES   # the name the templates and card_image.py read: the five, in the brand's order


def series_colors(n, highlight=None):
    """The colors of a chart of n series, by the brand (docs/brand.md, section 2). Up to five: ink, cardinal, blue,
    grey, light grey. More than five: the eight of "Many series" in order, past the eighth again from the first; with
    `highlight` (a series' index) that series is cardinal and the others take the eight, skipping the sixth (#AA3377,
    1.54 to 1 against cardinal). A series is never told by its color alone: each is named in the legend."""
    if n <= 5:
        return BRAND_SERIES[:n]
    pool = MANY_SERIES if highlight is None else [c for c in MANY_SERIES if c != "#AA3377"]
    out, k = [], 0
    for i in range(n):
        if i == highlight:
            out.append(ACCENT)
        else:
            out.append(pool[k % len(pool)])
            k += 1
    return out
SIZES = {"email": (1200, 750), "social_wide": (1200, 627), "social_square": (1080, 1080)}
SERIF = ["Georgia", "Times New Roman", "DejaVu Serif", "serif"]
SANS = ["Segoe UI", "Helvetica", "Arial", "DejaVu Sans", "sans-serif"]


def fmt(v):
    """A number as the site writes it: thousands commas, at most two decimals."""
    if v is None or (isinstance(v, float) and math.isnan(v)):
        return ""
    if float(v).is_integer():
        return f"{int(v):,}"
    return f"{v:,.2f}".rstrip("0").rstrip(".")


def mark_of(spec):
    """Session 533 (the Roundup audit's fix 11: the chart of the week named a number its chart did not show): the
    spec's mark, read against its own series. Returns {series, at, x, y, value, text} or None. x is the point's place
    on the x axis as the option writes it (the category's label, the timestamp, or the scatter's number); value is the
    series' own value there, never one supplied with the mark; y is where the ring sits: the value, or for a stacked bar
    the top of its segment. A mark whose series or place does not hold a number is not drawn."""
    m = spec.get("mark")
    if not m:
        return None
    series = spec["series"]
    i, j = m.get("series"), m.get("at")
    if not isinstance(i, int) or not isinstance(j, int) or not 0 <= i < len(series) or not 0 <= j < len(spec["x"]):
        return None
    vals = series[i]["values"]
    if j >= len(vals) or vals[j] is None or (isinstance(vals[j], float) and math.isnan(vals[j])):
        return None
    value = float(vals[j])
    y = value
    if spec["kind"] == "bar" and spec.get("stacked"):
        y = sum(float(s["values"][j]) for s in series[:i + 1]
                if j < len(s["values"]) and s["values"][j] is not None and not (isinstance(s["values"][j], float) and math.isnan(s["values"][j])))
    text = m.get("label") or fmt(value)
    if m.get("key"):
        text = f"{text}, {m['key']}"
    return {"series": i, "at": j, "x": spec["x"][j], "y": y, "value": value, "text": text,
            "label": m.get("label") or fmt(value), "key": m.get("key", "")}


def mark_point(m):
    """The mark as an ECharts markPoint: a cardinal ring on the point, its name the figure and its key (the site's SVG
    reader, site/lib/svgoption.ts, draws a markPoint's coord and name; ECharts itself draws the ring and the label)."""
    return {"symbol": "circle", "symbolSize": 12, "silent": True,
            "itemStyle": {"color": PAPER, "borderColor": ACCENT, "borderWidth": 2},
            "label": {"show": True, "formatter": m["text"], "position": "top", "distance": 8, "color": ACCENT, "fontSize": 11},
            "data": [{"coord": [m["x"], m["y"]], "name": m["text"], "value": m["value"]}]}


def echarts(spec):
    """The ECharts option for the site. Colors are the house palette (the site's tokens hold the same values)."""
    kind, series = spec["kind"], spec["series"]
    has_y2 = any(s.get("y2") for s in series)
    axis_style = {"axisLine": {"lineStyle": {"color": RULE}}, "axisTick": {"lineStyle": {"color": RULE}},
                  "axisLabel": {"color": MUTED, "fontSize": 11}, "splitLine": {"lineStyle": {"color": RULE}},
                  "nameTextStyle": {"color": MUTED, "fontSize": 11}}
    if kind == "scatter":
        x_axis = dict(axis_style, type="value", name=spec.get("x_label", ""), nameLocation="middle", nameGap=26, scale=True)
    elif spec.get("x_time"):
        x_axis = dict(axis_style, type="time", name=spec.get("x_label", ""))
    else:
        x_axis = dict(axis_style, type="category", data=spec["x"], name=spec.get("x_label", ""), nameLocation="middle",
                      nameGap=30,
                      axisLabel=dict(axis_style["axisLabel"], hideOverlap=True))
    y_axes = [dict(axis_style, type="value", name=spec.get("y_label", ""), scale=kind != "bar")]
    if has_y2:
        y_axes.append(dict(axis_style, type="value", name=spec.get("y2_label", ""), scale=True,
                           splitLine={"show": False}))
    out = []
    colors = series_colors(len(series), spec.get("highlight"))
    for i, s in enumerate(series):
        color = s.get("color") or colors[i]
        if kind == "scatter":
            data = [[x, y] for x, y in zip(spec["x"], s["values"]) if x is not None and y is not None]
        elif spec.get("x_time"):
            data = [[x, y] for x, y in zip(spec["x"], s["values"])]
        else:
            data = s["values"]
        e = {"name": s["name"], "type": kind, "data": data, "itemStyle": {"color": color},
             "yAxisIndex": 1 if s.get("y2") else 0}
        if kind == "line":
            e.update(showSymbol=len(spec["x"]) <= 40, symbolSize=5, lineStyle={"width": 2, "color": color})
        if kind == "bar" and spec.get("stacked"):
            e["stack"] = "total"
        if kind == "scatter":
            e["symbolSize"] = 7
        m = mark_of(spec)
        if m and m["series"] == i:
            e["markPoint"] = mark_point(m)
        out.append(e)
    option = {
        "color": colors, "backgroundColor": "transparent",
        "textStyle": {"fontFamily": "system-ui, sans-serif", "color": INK},
        "grid": {"left": 56, "right": 56 if has_y2 else 20, "top": 40, "bottom": 70 if spec.get("x_time") else 48,
                 "containLabel": True},
        "tooltip": {"trigger": "item" if kind == "scatter" else "axis", "backgroundColor": PANEL, "borderColor": RULE,
                    "textStyle": {"color": INK, "fontSize": 12}, "confine": True},
        "legend": {"show": len(series) > 1, "top": 0, "textStyle": {"color": MUTED, "fontSize": 11}},
        "toolbox": {"right": 4, "top": 0, "itemSize": 13, "iconStyle": {"borderColor": MUTED},
                    "feature": {"saveAsImage": {"title": "PNG", "name": spec.get("name", "erw-analysis"),
                                                "backgroundColor": PANEL, "pixelRatio": 2}}},
        "xAxis": x_axis, "yAxis": y_axes if has_y2 else y_axes[0], "series": out,
    }
    if spec.get("x_time"):
        option["dataZoom"] = [{"type": "inside"}, {"type": "slider", "height": 18, "bottom": 8}]
    return option


def _mark(fig, x, y, h):
    """The ERW mark (docs/brand/erw-mark.svg, session 25) at figure coordinates (x, y) = its top right corner, h = its
    height in figure units: a cardinal square whose white stem and three bars (14, 11 and 17 of 32 units) make an E
    that is also a bar chart, with "ERW" in Georgia to its left."""
    from matplotlib.patches import FancyBboxPatch, Rectangle
    w_px, h_px = fig.get_size_inches() * fig.dpi
    w = h * h_px / w_px
    u, v = w / 32, h / 32  # one unit of the 32 by 32 SVG grid, across and down
    fig.patches.append(FancyBboxPatch((x - w, y - h), w, h, boxstyle=f"round,pad=0,rounding_size={3 * v}",
                                      transform=fig.transFigure, color=ACCENT, zorder=5, mutation_aspect=w_px / h_px))
    for rx, ry, rw, rh in ((8, 7, 3, 18), (8, 7, 14, 3), (8, 14, 11, 3), (8, 22, 17, 3)):
        fig.patches.append(Rectangle((x - w + rx * u, y - (ry + rh) * v), rw * u, rh * v, transform=fig.transFigure,
                                     color="#FFFFFF", zorder=6, linewidth=0))
    size = h * h_px * 0.62 * 72 / fig.dpi
    fig.text(x - w - 0.006, y - h / 2, "ERW", ha="right", va="center", color=ACCENT, family=SERIF,
             fontsize=size * 0.9)


def png(spec, path, size="email"):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.dates as mdates
    import matplotlib.pyplot as plt
    import pandas as pd
    from matplotlib import font_manager
    w, h = SIZES[size]
    dpi = 100
    have = {f.name for f in font_manager.fontManager.ttflist}
    serif = next((f for f in SERIF if f in have), "serif")
    sans = next((f for f in SANS if f in have), "sans-serif")
    import textwrap
    scale = {"email": 1.0, "social_wide": 1.05, "social_square": 1.2}[size]
    fig = plt.figure(figsize=(w / dpi, h / dpi), dpi=dpi, facecolor=PAPER)
    px = lambda pt: pt * dpi / 72  # noqa: E731  a point size in pixels
    left_px, mark_px = 0.04 * w, 56 * scale  # the text starts at 4% of the width; the mark takes the top right

    def block(text, pt, width_px, family, color, y, lh=1.25):
        """Wrapped text from y (pixels from the top) down; returns the y below it."""
        chars = max(20, int(width_px / (px(pt) * (0.5 if family == serif else 0.52))))
        for line in textwrap.wrap(text, chars):
            fig.text(left_px / w, 1 - y / h, line, family=family, fontsize=pt, color=color, va="top", ha="left")
            y += px(pt) * lh
        return y

    # top down, in pixels: the title (clear of the mark), the subtitle, the legend row, then the axes
    y = 0.035 * h
    # session 533: the title stops short of the whole mark, the word "ERW" as well as its square (a title of 47
    # characters ran into the word on the 1080 px square of 2026-W39)
    y = block(spec["title"], 24 * scale, w - left_px - 2.6 * mark_px - 0.05 * w, serif, INK, y, 1.2)
    if spec.get("subtitle"):
        y = block(spec["subtitle"], 13 * scale, w - 2 * left_px, sans, MUTED, y + 4)
    _mark(fig, 0.965, 0.965, mark_px * 0.8 / h)
    kind, series = spec["kind"], spec["series"]
    legend_y = y + 6
    ncol = min(5, len(series) + (1 if any(s_.get("y2") for s_ in series) else 0))
    if len(series) > 1:
        y += px(11 * scale) * 1.55 * math.ceil(len(series) / ncol) + 4
    src_lines = textwrap.wrap(spec["source"], max(40, int((w - 2 * left_px) / (px(10 * scale) * 0.52))))
    rotated = kind == "bar" and len(spec["x"]) > 8
    # session 533: a rotated label longer than a month's ('2026-08') takes more room below the axis (a week's first day,
    # '2026-09-20', put the axis's own label on the source line); a month's and shorter keep the 92 they had
    longest = max((len(str(v)) for v in spec["x"]), default=0)
    bottom_px = (0.03 * h + len(src_lines) * px(10 * scale) * 1.3
                 + ((92 + 7 * max(0, longest - 7)) if rotated else 50) * scale)
    top_px = y + 18 * scale
    has2 = any(s_.get("y2") for s_ in series)
    ax = fig.add_axes([0.085, bottom_px / h, (0.81 if has2 else 0.875), 1 - (top_px + bottom_px) / h])
    ax.set_facecolor(PAPER)
    ax2 = ax.twinx() if any(s.get("y2") for s in series) else None
    x = spec["x"]
    if spec.get("x_time"):
        x = pd.to_datetime(pd.Series(x), utc=True).dt.tz_localize(None).tolist()
    n = len(series)
    colors = series_colors(n, spec.get("highlight"))
    for i, s in enumerate(series):
        color = s.get("color") or colors[i]
        a = ax2 if s.get("y2") else ax
        vals = [float("nan") if v is None else v for v in s["values"]]
        if kind == "line":
            a.plot(x, vals, color=color, lw=2.2, label=s["name"], marker="o" if len(x) <= 40 else None, ms=4)
        elif kind == "scatter":
            a.scatter(x, vals, color=color, s=22, alpha=0.8, label=s["name"])
        else:
            pos = list(range(len(x)))
            if spec.get("stacked"):
                base = [0.0] * len(x)
                for j in range(i):
                    base = [b + (0 if math.isnan(v) else v) for b, v in
                            zip(base, [float("nan") if q is None else q for q in series[j]["values"]])]
                a.bar(pos, vals, bottom=base, color=color, label=s["name"], width=0.75)
            else:
                wd = 0.8 / n
                a.bar([p - 0.4 + wd * (i + 0.5) for p in pos], vals, width=wd, color=color, label=s["name"])
    if kind == "bar":
        ax.set_xticks(range(len(x)))
        step = max(1, math.ceil(len(x) / 14))
        ax.set_xticklabels([str(v) if k % step == 0 else "" for k, v in enumerate(x)], rotation=0 if len(x) <= 8 else 45,
                           ha="center" if len(x) <= 8 else "right")
    if kind == "line" and not spec.get("x_time") and len(x) > 14 and all(isinstance(v, str) for v in x):
        # session 326: text on the x axis (a week's or month's label) is a category axis that labels every point, so the
        # dry Roundup of week 42 printed 107 dates over each other; label about ten, as the bars do
        step = max(1, math.ceil(len(x) / 10))
        ax.set_xticks([k for k in range(len(x)) if k % step == 0])
        ax.set_xticklabels([x[k] for k in range(len(x)) if k % step == 0])
    if spec.get("x_time"):
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %d" if len(x) < 400 else "%Y-%m"))
    for a in [ax] + ([ax2] if ax2 else []):
        for side in ("top", "right") if a is ax and not ax2 else ("top",):
            a.spines[side].set_visible(False)
        for side in ("left", "bottom", "right"):
            a.spines[side].set_color(RULE)
        a.tick_params(colors=MUTED, labelsize=11 * scale)
        a.grid(axis="y", color=RULE, lw=0.8) if a is ax else None
        a.set_axisbelow(True)
    from matplotlib.ticker import FuncFormatter
    for a in [ax] + ([ax2] if ax2 else []):
        a.yaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt(round(v, 2))))
    if kind == "scatter":
        ax.xaxis.set_major_formatter(FuncFormatter(lambda v, _: fmt(round(v, 2))))
    m = mark_of(spec)
    if m:  # session 533: the value the finding names, ringed in cardinal, with the figure and its key beside it
        a = ax2 if series[m["series"]].get("y2") else ax
        wd = 0.8 / n

        def where(k, si):
            """Where the k-th value of series si sits on the x axis, in the axis's own numbers."""
            if kind == "bar":
                return k if spec.get("stacked") else k - 0.4 + wd * (si + 0.5)
            if kind == "line" and not spec.get("x_time") and isinstance(x[k], str):
                return k  # a category axis of text: matplotlib places the k-th label at k
            return mdates.date2num(x[k]) if spec.get("x_time") else x[k]

        xm = where(m["at"], m["series"])
        a.scatter([mdates.num2date(xm) if spec.get("x_time") else xm], [m["y"]], s=(11 * scale) ** 2, facecolor=PAPER,
                  edgecolor=ACCENT, linewidth=2.2, zorder=6)
        a.get_xlim(), a.get_ylim()  # the limits as drawn, the ring included, before the label's place is chosen
        to_ax = a.transData + a.transAxes.inverted()
        fx, fy = to_ax.transform((xm, m["y"]))
        box = a.get_window_extent()
        aw, ah = box.width, box.height
        # the label's size in axes fractions: the figure (bold) and its key, one line each
        lw = (max(len(m["label"]) * px(12.5 * scale) * 0.6, len(m["key"]) * px(10.5 * scale) * 0.52) + 14) / aw
        lh = (px(12.5 * scale) + px(10.5 * scale)) * 1.35 / ah
        gap = 8 / ah
        # what else the axis draws, in axes fractions: each point of a line, each bar's span from its base to its top
        marks_at = []
        for si, s_ in enumerate(series):
            if bool(s_.get("y2")) != (a is ax2):
                continue
            base = [0.0] * len(x)
            if kind == "bar" and spec.get("stacked"):
                for q in series[:si]:
                    base = [b + (0.0 if v is None or (isinstance(v, float) and math.isnan(v)) else float(v)) for b, v in zip(base, q["values"])]
            for k, v in enumerate(s_["values"][:len(x)]):
                if v is None or (isinstance(v, float) and math.isnan(v)) or (k == m["at"] and si == m["series"]):
                    continue
                px_, top = to_ax.transform((where(k, si), base[k] + float(v)))
                if kind == "bar":
                    _, bot = to_ax.transform((where(k, si), base[k]))
                    half = (wd if not spec.get("stacked") else 0.75) / 2 * abs(to_ax.transform((1, 0))[0] - to_ax.transform((0, 0))[0])
                    marks_at.append((px_ - half, px_ + half, min(bot, top), max(bot, top)))
                else:
                    marks_at.append((px_, px_, top, top))

        def span(left):
            return (fx - 0.01 - lw, fx) if left else (fx, fx + 0.01 + lw)

        def hits(left, up, lift=0.0):
            x0, x1 = span(left)
            y0, y1 = (fy + gap + lift, fy + gap + lift + lh) if up else (fy - gap - lift - lh, fy - gap - lift)
            out = 1000 if (x0 < 0 or x1 > 1 or y0 < 0 or y1 > 1) else 0  # past the axes: the last resort
            return out + sum(1 for a0, a1, b0, b1 in marks_at if a1 >= x0 and a0 <= x1 and b1 >= y0 and b0 <= y1)

        def clear(left, up):
            """How much further than beside the ring the label must sit to clear what the axis draws under it."""
            x0, x1 = span(left)
            near = [(b0, b1) for a0, a1, b0, b1 in marks_at if a1 >= x0 and a0 <= x1]
            if up:
                return max([0.0] + [b1 - fy for b0, b1 in near if b1 > fy])
            return max([0.0] + [fy - b0 for b0, b1 in near if b0 < fy])

        prefer_left = fx > 0.6
        tries = []
        for left in (prefer_left, not prefer_left):
            for up in (True, False):
                tries.append((left, up, 0.0))
        tries += [(t[0], t[1], clear(t[0], t[1])) for t in list(tries) if clear(t[0], t[1]) > 0]
        # the fewest crossings; beside the ring before set apart from it (then joined to it by a hairline)
        left, up, lift = min(tries, key=lambda t: (hits(*t), t[2] > 0, tries.index(t)))
        dx, ha = (-12, "right") if left else (12, "left")
        halo = {"boxstyle": "square,pad=0.15", "fc": PAPER, "ec": "none", "alpha": 0.9}
        xy = (mdates.num2date(xm) if spec.get("x_time") else xm, m["y"])
        lift_pt = lift * ah * 72 / dpi * (1 if up else -1)
        for text, off, color, pt, weight in ((m["label"], (22 if up else -8), ACCENT, 12.5, "bold"),
                                             (m["key"], (8 if up else -24), MUTED, 10.5, "normal")):
            if text:
                a.annotate(text, xy, xytext=(dx, off + lift_pt), textcoords="offset points", ha=ha,
                           va="bottom" if up else "top", color=color, fontsize=pt * scale, family=sans,
                           fontweight=weight, bbox=halo, zorder=7)
        if lift > 0:  # the hairline from the ring to the label set apart from it
            a.annotate("", xy, xytext=(dx * 0.5, (6 if up else -6) + lift_pt), textcoords="offset points",
                       arrowprops={"arrowstyle": "-", "color": ACCENT, "lw": 0.9, "shrinkA": 0, "shrinkB": 7 * scale},
                       zorder=7)
    ax.set_ylabel(spec.get("y_label", ""), color=MUTED, fontsize=11 * scale, family=sans)
    if ax2:
        ax2.set_ylabel(spec.get("y2_label", ""), color=MUTED, fontsize=11 * scale, family=sans)
    if spec.get("x_label"):
        ax.set_xlabel(spec["x_label"], color=MUTED, fontsize=11 * scale, family=sans)
    if n > 1 or ax2:
        hs, ls = ax.get_legend_handles_labels()
        if ax2:
            h2, l2 = ax2.get_legend_handles_labels()
            hs, ls = hs + h2, ls + l2
        fig.legend(hs, ls, frameon=False, fontsize=10.5 * scale, labelcolor=INK, ncol=ncol,
                   loc="upper left", bbox_to_anchor=(left_px / w - 0.008, 1 - legend_y / h))
    yb = 0.03 * h + (len(src_lines) - 1) * px(10 * scale) * 1.3
    for line in src_lines:  # the source line, burned in at the bottom
        fig.text(left_px / w, yb / h, line, family=sans, fontsize=10 * scale, color=MUTED, va="bottom", ha="left")
        yb -= px(10 * scale) * 1.3
    os.makedirs(os.path.dirname(path), exist_ok=True)
    fig.savefig(path, dpi=dpi, facecolor=PAPER)
    plt.close(fig)
    return path
