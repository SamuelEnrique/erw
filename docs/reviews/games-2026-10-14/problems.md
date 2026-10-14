# The problem sets (`/learn/problems`): review of 14 October 2026

Energy Research Warehouse (ERW), session 279. Read end to end on a local production build of `wip/279-games` (session 261's fixes merged with `origin/main` at `eb64c7a5`): the index and the five sets, every answer opened, at 1280 and 390 px. Screens: `problems/before/` (22) and `problems/after/` (22). Session 261's review of 13 October is the base.

## What it is, and for whom

- Five sets of five questions: know your grid; prices and your bill; when the grid broke; storage and taxes; networks and money. Each question names its tables; "Show answer" opens the answer, a worked solution and why it matters. Every figure is computed from the warehouse when the page is built.
- For whom: an undergraduate class and its teacher (each set opens "For teachers"). Sets B and E also suit an investor learning the vocabulary. Nothing here is for an operator.
- **What it teaches, in one line:** how to get from a table of the grid's own data to a number, and why that number matters.

## Can a first-time user finish it without help?

- **Reading: yes.** 25 of 25 answers open, on both widths.
- **Answering before looking: not from the page alone.** The tables link to their line on `/data`, whose download is the whole table; the page does not say which rows to take.
- **The answers moved overnight, as session 261 warned.** Set A question 1 read "2026-10-12 ... ERCOT's peak was 2.56 times CAISO's" on 13 October; today it reads "2026-10-13: ERCOT 81,154 MW, CAISO 27,755 MW; ERCOT's peak was 2.92 times CAISO's". Correct both days; a class that prepared yesterday meets other numbers today (README question 8).
- The ratio questions' word order ("how many times CAISO's was ERCOT's?") still reads backwards to a student (A1, A3, C1, C5).

## Bugs, dead ends, numbers, layout

Numbers: `check-values.mjs`: **the five sets' values all match Supabase** (part of 100 of 100 on the Games pages, before and after). By hand from today's page: 81,154 / 27,755 = 2.92; 12,382,219.96 / 61,312.70 = 201.95. No wrong number.

| # | What | Where | Status |
|---|---|---|---|
| 1 | **Set B, question 2 asks about "all six ISO hubs" and lists seven**, two named "CAISO"; the answer's "smallest CAISO, -0.27 USD/MWh" does not say which zone | `after/03-prices-and-your-bill-answers-open-desktop.png` | open: an answer's words (README question 4) |
| 2 | The same question takes October 2026, now 14 days old ("months may be partial") | the same | open: an answer |
| 3 | Set B question 5 and set D question 3 use the latest month of the hour-of-day profile without saying it is partial | `after/05-storage-and-taxes-answers-open-390.png` | open: an answer (question 5) |
| 4 | **Set E question 5 compares the storm's 18 days with one normal week**: 201.95 times; day for day about 79 | `after/06-networks-and-money-answers-open-desktop.png` | open: an answer (question 6) |
| 5 | The ratio questions' word order | A1, A3, C1, C5 | open: words (question 7) |
| 6 | The worked solution of set B question 2 numbers each hub as a step | the same | open: small |
| 7 | The notes for teachers name `/mix`, `/emissions`, `/network`, `/grid/ercot`, `/grid/caiso`: each answers by redirect to a view of `/grid` | every set | open: they work |
| 8 | **The Games menu lists four of the five sets** (storage and taxes is missing) and not the index | `site/lib/pages.ts` | open: the menu is outside this session (question 14) |
| 9 | Units in the mono face with a space before the percent sign | every set | open: brand, small |
| 10 | The site menu's closed dropdown measures 418 px at 390 px; the page does not scroll sideways | every 390 px screen | not the tab's files |

Not broken: no page error, no "NaN", "Infinity", "undefined" or "null" in any text, no sideways scroll at 390 px, all 32 of the sets' own links answer (four by redirect).

## Against the brand (`docs/brand.md`)

- The index and the set pages draw inside `<Brand>` since session 261's commit `46fd7338` (on this branch, not on main): white page, serif titles, links underlined.
- Still off: units in mono, and the "For teachers" note marked by a cardinal bar (a fourth job for the accent).

## Henry's review

- His ten questions are about the game's battery. None is about the problem sets. Set D's questions 1 and 3 use the game's battery (90 percent round trip, 13.5 kWh): if his answers change those defaults, the two answers move with them by themselves.
- Kelsey's conversation of 5 October: still nothing in the repository (README question 13).

## Done for real users

| # | What | Effort |
|---|---|---|
| 1 | Samuel's rulings on bugs 1 to 5 (README questions 4 to 7), then the changes to `site/lib/problems.ts` and its tests | S |
| 2 | A dated edition of each set at its own address, beside the live one (question 8) | M |
| 3 | The rows a question needs, under it, as a small table or a CSV of just those rows | M |
| 4 | The menu: the fifth set and the index (question 14) | S |
| 5 | A teacher's copy: answers closed for students, or a printable page | M |
| 6 | The notes for teachers at today's addresses | S |
| 7 | The brand's remainder: units in the text face, the teacher's note without the cardinal bar | S |
| 8 | One teacher tries a set with a class | M |
| 9 | The release lines set to `live`, with rule 8's snapshot | S |

## Fixes made on the branch in this session

None: nothing plainly broken was found that needs no ruling. No question and no answer changed; `site/lib/problems.ts` is untouched.
