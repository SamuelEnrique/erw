"""House style for Automated Analysis (platform tool 26): one chart spec, three sizes.

Energy Research Warehouse (ERW), session 23. Every template's render() builds a chart spec (a plain
dict) and hands it here:

    spec = {"kind": "line" | "bar" | "scatter",
            "title": ..., "subtitle": ..., "source": "the source line",
            "x": [...] (category labels or ISO timestamps; scatter: numbers),
            "x_label": ..., "y_label": ..., "x_time": bool, "stacked": bool,
            "series": [{"name": ..., "values": [...], "y2": bool (optional, a second axis)}],
            "y2_label": ... (optional)}

    echarts(spec)                 the site's interactive chart: an ECharts option (JSON), in the site's tokens
    png(spec, path, "email")      1200 x 750 px, shown at 600 px in the email
    png(spec, path, "social_wide")    1200 x 627 px
    png(spec, path, "social_square")  1080 x 1080 px

The look: the Stanford palette the site uses (cardinal #8C1515 first, then Lagunita, Poppy, Palo Alto,
Plum, Bay, Sky), titles in Georgia, the ERW mark (the site's icon, a cardinal square with an E, and
"ERW") at the top right, and the source line burned into the bottom of every PNG, so a chart that
travels without its page still names its source.
"""

import math
import os

PAPER, INK, ACCENT, MUTED, RULE, PANEL = "#F7F3EA", "#2E2D29", "#8C1515", "#6B665E", "#D9D2C3", "#FBF8F2"
PALETTE = ["#8C1515", "#007C92", "#E98300", "#175E54", "#620059", "#6FA287", "#4298B5", "#B6B1A9", "#8F993E", "#651C32"]
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
        x_axis = dict(axis_style, type="category", data=spec["x"], name=spec.get("x_label", ""),
                      axisLabel=dict(axis_style["axisLabel"], hideOverlap=True))
    y_axes = [dict(axis_style, type="value", name=spec.get("y_label", ""), scale=kind != "bar")]
    if has_y2:
        y_axes.append(dict(axis_style, type="value", name=spec.get("y2_label", ""), scale=True,
                           splitLine={"show": False}))
    out = []
    for i, s in enumerate(series):
        color = s.get("color") or PALETTE[i % len(PALETTE)]
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
        out.append(e)
    option = {
        "color": PALETTE, "backgroundColor": "transparent",
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
    """The ERW mark at figure coordinates (x, y) = its top right corner, h = its height in figure units."""
    from matplotlib.patches import Rectangle
    w_px, h_px = fig.get_size_inches() * fig.dpi
    w = h * h_px / w_px
    fig.patches.append(Rectangle((x - w, y - h), w, h, transform=fig.transFigure, color=ACCENT, zorder=5))
    size = h * h_px * 0.62 * 72 / fig.dpi
    fig.text(x - w / 2, y - h * 0.52, "E", ha="center", va="center", color=PAPER, family=SERIF, fontsize=size, zorder=6)
    fig.text(x - w - 0.006, y - h / 2, "ERW", ha="right", va="center", color=ACCENT, family=SERIF,
             fontsize=size * 0.9, weight="bold")


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
    y = block(spec["title"], 24 * scale, w - left_px - mark_px - 0.07 * w, serif, INK, y, 1.2)
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
    bottom_px = 0.03 * h + len(src_lines) * px(10 * scale) * 1.3 + (92 if rotated else 50) * scale
    top_px = y + 18 * scale
    has2 = any(s_.get("y2") for s_ in series)
    ax = fig.add_axes([0.085, bottom_px / h, (0.81 if has2 else 0.875), 1 - (top_px + bottom_px) / h])
    ax.set_facecolor(PAPER)
    ax2 = ax.twinx() if any(s.get("y2") for s in series) else None
    x = spec["x"]
    if spec.get("x_time"):
        x = pd.to_datetime(pd.Series(x), utc=True).dt.tz_localize(None).tolist()
    n = len(series)
    for i, s in enumerate(series):
        color = s.get("color") or PALETTE[i % len(PALETTE)]
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
