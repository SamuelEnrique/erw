# Session 241, batch B: the pages of words on the brand

Screenshots of the pages of batch B in the internal view, a local build of branch `wip/241b-brand`, 13 October 2026,
after only. Each is the page's first 2,200 px at 1280 px wide (`<page>_1280.png`) and its first 2,600 px at 390 px
(`<page>_390.png`), quantized to a 32-color palette to keep this folder under 4 MB. The originals, every page of the
capture (36 addresses and 7 of Thesis Builder at both widths) and the text of each page before and after are in
`runs/session241b/` in the main copy, not in git.

What every page changed by: the brand's wrapper (`<Brand>`), so the page is white, its title is Source Serif 4 in
ink, its text IBM Plex Sans, its figures and code IBM Plex Mono, a link in running text is underlined, a table has
one dark rule under its header and no band. No word, number, link or control changed: 34 of the 36 addresses compare
to 0 lines of difference with the build of the commit before (`numbers_text_before_after.txt`); the two others are
internal and differ by data: `/internal/waits` lists this session's own report and `/internal/usage` shows live counts.

| Files | Page | What was changed | What still looks off |
|---|---|---|---|
| `about_*` | `/about` | wrapper; a line of text stops at 68 characters; the links of "The site" underlined | the group names of "The site" are small grey labels in the letters they are written in ("Economics"), no longer capitals |
| `terms_*`, `privacy_*` | `/terms`, `/privacy` | wrapper; the light rule above each section title; the registry's table by the brand's table rules | the registry is one long table (some 9,600 px) |
| `data_*` | `/data` | wrapper; the catalogue's rows counts in the mono face; the install commands on fog | "model-extracted" is cardinal words that are no link; at 390 px the catalogue is a wide table that scrolls sideways, with tall rows, as before |
| `data_standard_*`, `data_methods_battery_stack_*`, `data_methods_storage_*` | `/data/standard`, two of the 69 method notes | the prose rules: title at 36 (24 on a phone), section headings at 24 (20) under a light rule, text at most 68 characters wide, tables as wide as they need with one dark rule under the header, code in mono on fog | a wide table sits beside narrow text: the text column is 68 characters and a table can be twice that |
| `data_faults_*` | `/data/faults` | wrapper; the titled blocks; the faults' table | nothing noted |
| `digest_*`, `digest_2026-10-10_*` | `/digest` (a digest's own page is the same article), a weekend's "No weekend issue" | the prose rules; the archive beside | the archive's links are all cardinal and underlined, a dense column |
| `roundup_*` | `/roundup` (a Roundup's own page is the same article) | the prose rules | in "Deals of the week" a date breaks over two lines ("2026-" and "10-05") where the table is nine columns in the article's width; below the first 2,200 px the page was not looked at |
| `subscribe_*` | `/subscribe` | wrapper; "Sign up" is the brand's one action (cardinal, white words); the address field in the text face; 16 px checkboxes in cardinal | the button sits under the topics at the left, not beside the field |
| `ask_*`, `ask_ercot_*` | `/ask`, `/ask/ercot` | wrapper; the question field in the text face | while the box is empty the "Ask" button is a pale cardinal with grey words; the panel of `/ask/ercot` is shared with the grid pages and is not edited, and no question was sent, so an answer and its chart were not looked at |
| `thesis_*`, `thesis_run_fixture-done_tab_trends_*`, `thesis_run_fixture-done_tab_capital_*` | `/thesis`: the real list of runs, and two tabs of a made-up run of the check's stand-in | wrapper; the tab in view names a token; the charts read the brand's tokens and face | a trend's title has a cardinal rule under it (the report's own class); two series are the mix's blue and orange; the marks ("differs", "run anyway") are in small letters; "none" and "not yet" are mono italics |
| `reports_draft_shape-premium_*`, `reports_draft_ai-gigawatts_*` | the two draft reports | wrapper; a line of text at 68 characters | the bars keep rounded ends and the price board's up and down colors |
| `in-review_*` | the page a visitor is shown for a page in review (here asked directly, for `/storage`) | wrapper; "Open now" is the shared section with the light rule above | with no page live the list holds "Home" alone |
| `internal_*` | the seven internal pages | wrapper only; "Open the internal view" is the brand's one action | they are tables for the owner: no further work |

Not shown: `/reports` (it answers 404: no page is at that address).
