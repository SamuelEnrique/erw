# Data requests from the licensing sweep (chain 229, lab-desktop third window)

Energy Research Warehouse (ERW). Written by chain 229 (`queue/done/229-day-13-november-desktop-window3-licenses.md`), from session 4102, 13 November 2026. The licensing sweep writes no warehouse data: each row is a change only the data machine's chain (window A, which holds the data lock) makes. Window A marks a row done with its commit.

| # | Requested (UTC) | Session | For | What | Why | State |
|---:|---|---|---|---|---|---|
| 1 | 2026-11-13 | 4102 | `warehouse/news/index.py` (the registry rows it writes to `warehouse/metadata/sources.csv`) | Fold an em or en dash in a news outlet's name to a hyphen before the name is written, and merge the row `IEA – International Energy Agency` (an en dash, first seen 2026-09-25) into `IEA - International Energy Agency` (a hyphen), its tables `news_index;news_stories` | The name is copied verbatim into `site/data/table_citations.json` and `docs/redivis/release-v1/tables.csv` whenever `package/tools/build_tables.py` or `warehouse/redivis/release_v1.py` runs; the repository writes no em or en dash | requested |
