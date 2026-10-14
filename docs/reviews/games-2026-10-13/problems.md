# The problem sets (`/learn/problems`): review of 13 October 2026

Energy Research Warehouse (ERW), session 261. Read end to end on a local production build of `origin/main` (`811328fe`): the index and the five sets, every answer opened, at 1280 and 390 px. Screens: `problems/before/` (22) and `problems/after/` (the same list after the fixes).

## What it is, and for whom

- Five sets of five questions, 25 in all: know your grid; prices and your bill; when the grid broke; storage and taxes; networks and money. Each question names its tables; "Show answer" opens the answer, a worked solution and a line on why it matters. Every figure is computed from the warehouse when the page is built.
- For whom: an undergraduate class and its teacher (each set opens with a note "For teachers": the minutes, the prerequisites, the pages to open). Sets B and E (prices and bills, networks and money) also suit an investor learning the vocabulary. Nothing here is for an operator.
- **What it teaches, in one line:** how to get from a table of the grid's own data to a number, and why that number matters.

## Can a first-time user finish it without help?

- **Reading it: yes.** 25 of 25 answers open, on both widths, without a script.
- **Answering before looking: no, not from the page alone.** Where a student gets stuck:
  1. The tables under each question link to that table's line on `/data`, which offers "Download CSV": the whole table (17,952 rows for the demand table). A student with a spreadsheet can do it; the page does not say how, and question 1 of set A needs 24 rows of it.
  2. **The answers move.** Each page is rebuilt from the latest data, so the day in set A's questions was 2026-10-12 today and will be another tomorrow. A teacher who prepares on Monday meets other numbers on Wednesday, and a student's saved answer is wrong by the next build. The page says so in one sentence; it offers no dated copy.
  3. The word order of the ratio questions: "how many times CAISO's was ERCOT's?" is answered "ERCOT's peak was 2.56 times CAISO's". Correct, and a student will read it the other way round. Four questions are built this way (A1, A3, C1 and C5).
- A student can open every answer at once: nothing separates the teacher's copy from the student's.

## Bugs, dead ends, numbers, layout

Numbers: `check-values.mjs` on the five sets: **73 of 73 match Supabase** (17, 12, 11, 21 and 12 by set). By hand from the page: 76,139 / 29,724 = 2.56; 40,198 / 19,409 = 2.07; 19,409 / 1,426,842 = 1.36 percent; 201,933 / 251,528 = 80.28 percent; (12.81 x 61.65 - 14.23 x 31.40) / 1,000 = 0.34 USD, times 10,000 homes 3,427.67; Louisiana 12.5 percent of 97,308 = 12,163.51. All as written. No wrong or stale number found. What is wrong is in the words around the numbers:

| # | What | Where | Fixed here |
|---|---|---|---|
| 1 | **Set B, question 2 asks about "all six ISO hubs" and lists seven**, two of them both named "CAISO" (0.71 and -0.27: its two zones, NP15 and SP15). The answer's "smallest CAISO" does not say which | `before/03-prices-and-your-bill-answers-open-desktop.png` | no: an answer's words |
| 2 | The same question takes "the latest month all hold", which is October 2026, thirteen days old, and MISO has been paused since 4 October, so its October is shorter still. It says "months may be partial" and compares them all the same | the same | no: an answer |
| 3 | **Set B question 5 and set D question 3 use October's hour-of-day profile and do not say the month is partial** (question 1 of the same set takes "the latest complete month", September) | `before/05-storage-and-taxes-answers-open-390.png` | no: an answer |
| 4 | **Set E, question 5 compares 18 days of Winter Storm Uri with one normal week** ("201.95 times as much"). Day for day it is about 79 times | `before/06-networks-and-money-answers-open-desktop.png` | no: an answer |
| 5 | The ratio questions' word order (above) | all sets | no: a question's words |
| 6 | The worked solution of set B question 2 numbers each hub as a step (steps 2 to 8 are seven hubs) | the same | no: small |
| 7 | The notes for teachers name addresses that have since moved: `/mix`, `/emissions`, `/network`, `/grid/ercot`. Each still answers, by redirect to a view of `/grid` | every set | no: they work |
| 8 | **The Games menu lists four of the five sets** (storage and taxes is missing) and not the index; the index is reached only from a set's breadcrumb. The bill explainer the sets lean on is under Economics | `site/lib/pages.ts` | no: outside this session's files |
| 9 | Units are set in the mono face with the figure and a space before the percent sign ("38.36 %") | every set | no: brand, small |

Not broken: no page error, no "NaN" or "Infinity" in any text (set A question 5 was repaired in session 149 and holds), no sideways scroll at 390 px, and all 32 links answer (four by redirect).

## Against the brand (`docs/brand.md`)

- Before: the old look (cream paper, the old text face), no `<Brand>` wrapper, on the index and on every set.
- After this session: the three page files draw inside `<Brand>`, as `/learn/bill` does. White page, the serif titles, links underlined, the rule above each question. Nothing else was restyled.
- Still off: units in mono (the brand keeps mono for figures in tables), and the "For teachers" note is marked by a cardinal bar, a fourth job for the accent.

## Henry's review and Kelsey's conversation

- **Henry:** his ten questions are about the battery game's battery. None is about the problem sets. Set D's questions 1 and 3 use the game's battery (90 percent round trip, 13.5 kWh): if his answers change those defaults, the two answers move with them, by themselves.
- **Kelsey's conversation of 5 October:** nothing of it is in the repository. Needs Samuel: what it asked of the problem sets, if anything.

## Done for real users

| # | What | Effort |
|---|---|---|
| 1 | Samuel's rulings on bugs 1 to 5 (README, questions 4 to 7), then the five changes to `site/lib/problems.ts` and its tests | S |
| 2 | A dated edition: each set frozen at a stated day with its own address, beside the live one, so a class answers what its teacher prepared (README, question 8) | M |
| 3 | The rows a question needs, on the page: a small table or a CSV of just those rows under each question, instead of the whole table's download | M |
| 4 | The menu: the fifth set, the index, and the bill explainer under Games (`site/lib/pages.ts`, the menu tests) | S |
| 5 | A teacher's copy: the answers closed for students, opened by a link the teacher holds, or a printable page | M |
| 6 | The notes for teachers name the pages by their names and today's addresses | S |
| 7 | The brand's remainder: units in the text face, the teacher's note without the cardinal bar | S |
| 8 | One teacher tries a set with a class, and what they report is fixed | M |
| 9 | The release lines in `site/lib/release.ts` set to `live`, with rule 8's snapshot | S |

## Fixes made on the branch

1. The index and the set page draw inside `<Brand>` (its own commit: it can be dropped without the others).

No question and no answer is changed: `site/lib/problems.ts` is untouched.
