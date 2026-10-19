# Session 314: the battery page's income chart, before and after

Energy Research Warehouse (ERW), 19 October 2026. The shots are of `/cost-of-power/battery` in the internal view on the
local build (before: the build of session 304's commit; after: this session's), at 1280 and 390 px. Each `chart_*` shot
is the chart alone (the figure element), so the fault and the fix are side by side.

What to look at:

- `chart_before_default_1280.png` and `chart_before_default_390.png`: the fault. "Income by stream" at `?it=chart`: the
  "Last twelve months" column is drawn as twelve thin bars over the USD axis (they are the axis's own ticks: the step
  list ended at 20,000, so an axis in tens of millions of dollars drew about 3,500 ticks, each with a grid line and a
  label), and the column sub-labels run into each other ("calendar yearcalendar year"). At 390 the chart is shrunk with
  its viewBox and scrolls sideways inside its frame.
- `chart_after_default_1280.png` and `chart_after_default_390.png`: four ticks (0, 20, 40, 60 million); the labels
  wrapped by words to their columns ("Last / twelve / months", "Your / window"); the sub-labels that fit written ("9
  months" under 2026), the others left to the hover and the table; the figure above each bar where it fits; the series'
  names at the top right spaced by their own length; the hatched note under the axis. At 390 the chart is drawn for the
  width it has (its text keeps its size), the labels are thinned to every other column, and nothing scrolls sideways.
- `chart_before_2y_*.png` and `chart_after_2y_*.png`: the same chart with the reader's window set to 2024 to 2025
  (`?it=chart&wf=2024&wt=2025`): the window column's sub-label is "2024 to 2025: the average year".
- `chart_after_years_*.png`: the year chart ("Revenue by year, USD per kW"), drawn through the same component: its
  axis (0 to 400) and labels are as before; at 390 every year is labelled, since "2018" fits a column.
- `norange8_after_*.png`: the line under "What matters most" at `?dur=8`: "No published range, so no row: capital cost
  (Lazard ... prints no 8-hour case, so the ATB's figure stands alone: USD 2,300 per kW ...); fixed O&M (...)" (the
  ruling of 19 October: 8 hours takes the ATB's figure alone).
- `page_before_*.png` and `page_after_*.png`: the whole page at `?it=chart` at both widths.

Every checked number on the page is what it was (`check-values`: the session's report).
