# The ERW mark

Session 25. An original mark, drawn for the ERW: a cardinal (#8C1515) square whose white stem and three bars of 14, 11 and 17 units form an E that is also a small bar chart, the warehouse's two jobs in one letter. The wordmark sets "ERW" in Georgia beside it. Both are plain SVG with no external assets.

| File | Use |
|---|---|
| `erw-mark.svg` | The mark alone: the site's favicon (`site/app/icon.svg`), the chart corner mark (`warehouse/analysis/style.py` draws the same geometry) |
| `erw-wordmark.svg` | The mark and "ERW": the site header (`site/components/Wordmark.tsx` inlines the same SVG) |

Emails draw the same geometry in HTML (`warehouse/news/email_digest.py`, `WORDMARK_HTML`), because mail clients strip inline SVG.
