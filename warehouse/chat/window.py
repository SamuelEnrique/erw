"""Session 5267 (chain 256): whether a window of a series is whole.

Energy Research Warehouse (ERW). A query bounded by a start and an end returns the rows it matched, their count and the
first and last time. It did not say how many steps the window should hold, so the chat found a short day, week or month
by counting the rows itself and by grouping them again: 79 of the 257 tool calls made after the figure was in hand on
13 November 2026 (docs/reviews/ask-eval-2026-11-13.md, "The calls after the figure, by class"). window_of says it with
the first result: the steps the window holds, the steps it has at the table's step, and the steps that are missing.

A pure function of the times read and the table's step: no table is read here and nothing is filled. The site's loop
holds the same in site/lib/chat/window.ts; tests/fixtures/session5267/window_cases.json holds both to the same answers
(tests/test_session5267_ask.py, site/scripts/test-ask-window.test.mjs).

    window_of(start, end, steps, series)

  start, end   the window as the query read it, two UTC instants ("2026-11-10T06:00:00Z"), start included, end not
  steps        the steps the rows may have: the rows' own freq values (the Python loop), or the steps the catalogue lists
               for the table (the site's loop, which reads no freq). One step is taken as it is. Of several, the step is
               the smallest gap between two neighbouring rows of a series, when that gap is one of them; else not known
  series       {"entity|variable": [the UTC instants of its rows in the window]}

The answer (None when no series is given):

  from, until        the window
  step               the step the count is made at, or None
  steps_held         the rows held in the window (of one series); with several series {"least": n, "most": n}
  steps_in_window    the steps the window has at that step, or None when the step is not known
  steps_missing      steps_in_window less steps_held (one series, a known step)
  whole              True, False, or None when it cannot be told
  first_held, last_held
  missing            the first runs of missing steps, each {"from", "until", "steps"} (until is the first step held after
                     the run, or the window's end), at most MISSING_SHOWN; missing_runs counts them all
  series             the number of series matched, when more than one
  note               what the answer may say. On a table of days or longer a whole window means every row is held: whether a
                     row covers its whole period is the table's own to say (WHOLE_ROWS)
"""
import calendar
import datetime as dt
import re

MISSING_SHOWN = 6
MOST_LABELS = 2400      # the months or years of a window counted one by one; a longer window is not judged
FIXED = {"P1D": 86400, "P1W": 604800}
CALENDAR = ("P1M", "P1Y")
UTC = dt.timezone.utc


def seconds_of(step):
    """The seconds of a step of fixed length ("PT5M" 300, "PT1H" 3600, "P1D" 86400, "P1W" 604800); None for a month, a
    year or a step this does not read."""
    if step in FIXED:
        return FIXED[step]
    m = re.fullmatch(r"PT(\d+)([MH])", step or "")
    if not m or int(m.group(1)) <= 0:
        return None
    return int(m.group(1)) * (60 if m.group(2) == "M" else 3600)


def _epoch(t):
    """A UTC instant as whole seconds since 1970."""
    if isinstance(t, (int, float)):
        return int(t)
    s = str(t).strip().replace("Z", "+00:00")
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", s):
        s += "T00:00:00+00:00"
    d = dt.datetime.fromisoformat(s)
    if d.tzinfo is None:
        d = d.replace(tzinfo=UTC)
    return int(d.timestamp())


def _iso(sec):
    return dt.datetime.fromtimestamp(sec, UTC).strftime("%Y-%m-%dT%H:%M:%SZ")


def _labels(step, a, b):
    """The month or year starts t with a <= t < b, as seconds; None when there are more than MOST_LABELS."""
    d = dt.datetime.fromtimestamp(a, UTC)
    y, m = d.year, (d.month if step == "P1M" else 1)
    out = []
    while True:
        t = calendar.timegm((y, m, 1, 0, 0, 0))
        if t >= b:
            return out
        if t >= a:
            out.append(t)
            if len(out) > MOST_LABELS:
                return None
        if step == "P1M":
            y, m = (y + 1, 1) if m == 12 else (y, m + 1)
        else:
            y += 1


def step_of(steps, series):
    """The one step the rows are counted at, or None: the only step given, or of several the smallest gap between two
    neighbouring rows of a series when it is one of them (a month's or a year's rows are told by their gap of 28 to 31
    days, or 365 or 366)."""
    uniq = sorted({s for s in (steps or []) if s})
    if len(uniq) == 1:
        return uniq[0]
    if not uniq:
        return None
    gap = None
    for times in series.values():
        for x, y in zip(times, times[1:]):
            if y > x and (gap is None or y - x < gap):
                gap = y - x
    if gap is None:
        return None
    for s in uniq:
        sec = seconds_of(s)
        if sec == gap or (s == "P1M" and 28 * 86400 <= gap <= 31 * 86400) or (s == "P1Y" and gap in (365 * 86400, 366 * 86400)):
            return s
    return None


def _expected(step, a, b, held):
    """(the steps the window [a, b) has, as a sorted list of seconds or a count; None when it cannot be told)."""
    if step in CALENDAR:
        return _labels(step, a, b)
    sec = seconds_of(step)
    if sec is None:
        return None
    if step == "P1W":
        if not held:
            return None                     # a week's row is dated the day its week begins, which only a row says
        anchor = held[0] % sec
    else:
        anchor = 0
    first = a + ((anchor - a) % sec)
    return (first, sec, 0 if first >= b else (b - 1 - first) // sec + 1)


def _one(step, a, b, times):
    """(steps held on the step's grid, steps in the window, the runs of missing steps) for one series; (n, None, None)
    when the step is not known or a row sits off the step's grid."""
    held = sorted(set(times))
    exp = _expected(step, a, b, held) if step else None
    if exp is None:
        return len(held), None, None
    runs = []
    if isinstance(exp, list):
        labels, have = exp, set(held)
        if not have <= set(labels):
            return len(held), None, None
        run = None
        for i, t in enumerate(labels):
            if t in have:
                if run:
                    runs.append({"from": _iso(run[0]), "until": _iso(t), "steps": run[1]})
                    run = None
            else:
                run = (t, 1) if run is None else (run[0], run[1] + 1)
        if run:
            runs.append({"from": _iso(run[0]), "until": _iso(b), "steps": run[1]})
        return len(held), len(labels), runs
    first, sec, n = exp
    if any((t - first) % sec for t in held):
        return len(held), None, None
    prev = first - sec
    for t in held:
        if t - prev > sec:
            runs.append({"from": _iso(prev + sec), "until": _iso(t), "steps": (t - prev) // sec - 1})
        prev = t
    last = first + (n - 1) * sec
    if n and prev < last:
        runs.append({"from": _iso(prev + sec), "until": _iso(b), "steps": (last - prev) // sec})
    return len(held), n, runs


WHOLE = "the window holds every step it has: steps_held of steps_in_window at the table's step. No count and no regrouping is needed to check it"
WHOLE_ROWS = ("every row of the window is held: steps_held of steps_in_window, one row a day, a week, a month or a year. No count and no regrouping is needed to check it. "
              "Whether a row covers its whole period is the table's own to say, in a variable that counts the hours or days behind the row where it has one (da_hours, days_held and the like)")
PART = ("the window is held in part: steps_held of steps_in_window. The steps under missing are not held and nothing is filled. "
        "Say so in the answer: a figure over this window is over the steps held, not over the whole window")
NONE_HELD = ("no step of the window is held for these filters: steps_in_window steps, none of them in the table. When the entity and the variable are "
             "right (the same query with no start and no end finds their rows), the table holds the series and not this window: say which window is "
             "missing and state no figure of it")
UNKNOWN = ("whether the window is whole cannot be told from the rows read (the table's step is not one a window is counted by, "
           "or the rows do not sit on one step): steps_held is the rows held")
SEVERAL = ("more than one series matched: steps_held gives the least and the most rows any one of them holds in the window. "
           "For the steps a series is missing, ask it alone (one entity, one variable)")
EMPTY = "the window has no step of the table inside it (it is shorter than the table's step, or starts and ends between two steps)"


def window_of(start, end, steps, series):
    """What a bounded window of a series holds beside what it has (the module's docstring). None when no series is given."""
    if not series:
        return None
    a, b = _epoch(start), _epoch(end)
    rows = {k: sorted(_epoch(t) for t in v) for k, v in series.items()}
    rows = {k: [t for t in v if a <= t < b] for k, v in rows.items()}
    step = step_of(steps, rows)
    out = {"from": _iso(a), "until": _iso(b), "step": step}
    every = sorted(t for v in rows.values() for t in v)
    if len(rows) == 1:
        held, n, runs = _one(step, a, b, next(iter(rows.values())))
        out.update({"steps_held": held, "steps_in_window": n})
        if n is not None:
            out["steps_missing"] = n - held
    else:
        each = [_one(step, a, b, v) for v in rows.values()]
        ns = {n for _, n, _ in each}
        n = ns.pop() if len(ns) == 1 else None
        runs = None
        out.update({"series": len(rows), "steps_held": {"least": min(h for h, _, _ in each), "most": max(h for h, _, _ in each)}, "steps_in_window": n})
        held = out["steps_held"]["least"]
    out["whole"] = None if n is None or n == 0 else held == n
    out["first_held"] = _iso(every[0]) if every else None
    out["last_held"] = _iso(every[-1]) if every else None
    if runs:
        out["missing"] = runs[:MISSING_SHOWN]
        out["missing_runs"] = len(runs)
    if n is None:
        note = UNKNOWN
    elif n == 0:
        note = EMPTY
    elif out["whole"]:
        note = WHOLE_ROWS if step in FIXED or step in CALENDAR else WHOLE      # a table of days or longer: a row may cover part of its period
    elif not every:
        note = NONE_HELD
    else:
        note = PART
    out["note"] = note + (". " + SEVERAL if len(rows) > 1 else "")
    return out
