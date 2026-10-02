---
role: data
spend_cap_usd: 3
timeout_minutes: 120
permission_mode: auto
---
# Probe: does CAISO publish available supply history for "how tight was it"?

Source: session 58's open question 2; PRIORITIES.md layer 1, order 4 (a new source). The health gate must be open when you start: `python warehouse/metadata/build_status.py --gate` exits 0. If it does not, stop and report why.

`/grid/caiso`'s Reliability section measures how tight a day was from demand alone (`caiso_reliability_daily`). The real measure is demand against available supply (capacity available plus imports). CAISO's Today's Outlook shows available supply live. This task finds out whether its history can be had, and builds nothing yet.

Do this, as a probe only:

1. Read `.claude/skills/erw-add-connector/SKILL.md` (step 1, "Probe before writing code"), and docs/price-sources.md for CAISO's terms.
2. Find where Today's Outlook takes its data (the page's own data files; CAISO serves them as CSV or JSON per day). Fetch at most 6 files in all:
   - one recent day;
   - one day 30 days back;
   - one in September 2022;
   - one in September 2020;
   - at most 2 others, if you need them to learn the naming.

   Save them under the scratch folder, never warehouse/output.
3. Record:
   - the exact URLs, the columns and units, and the interval;
   - how far back the history goes;
   - whether, for 2022-09-06's 17:00 to 18:00 Pacific hour, available supply is above that hour's 51,104 MW demand.
4. Check CAISO's terms of use for redistributing these files.
5. Write `docs/methods/caiso_available_supply_probe.md` with the findings and a recommendation: either build a connector (with its table name, its shape, and a ceiling for the backfill), or do not, and say why.

No warehouse writes, no upload, no Supabase load: this is a probe. Commit the probe document. No em dashes.
