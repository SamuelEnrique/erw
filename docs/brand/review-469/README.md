# Session 469: /policy, before and after

Energy Research Warehouse (ERW), 21 October 2026. Each shot is the window (not the whole page) at 1280 and at 390 px,
taken with `site/scripts/shot.mjs` in the internal view.

- `before/policy_1280.png`, `before/policy_390.png`: production at about 10:00 UTC, the page as it stood.
- `after/policy_1280.png`, `after/policy_390.png`: the local build of `wip/469-policy` at about 10:08 UTC; the first
  screen is as before (nothing on it changes).
- `after/policy_group_1280.png`, `after/policy_group_390.png`: `/policy?tag=loads_interconnection_tariffs`, the new
  choice of the Tag filter, with the significance floor lifted to "All".

What to look at: the Tag filter's new choice, "Large loads, interconnection or tariffs", and the count of actions it
lists; and, in a row opened by a click, the line "Figures: ..." under the read, or "No figure: this read states no
number". The opened row cannot be shot by `shot.mjs` (it loads, it does not click); `site/scripts/check-policy-reads.mjs` opens one in a browser and reads the line.
