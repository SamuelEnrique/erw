# Session 10412 report: chain 720, part E: the equities page's problem set, on what companies filed

Energy Research Warehouse (ERW). 27 November 2026, 11:37 to 11:57 UTC, the portable laptop's first window (code role), unattended.

## What was built (`wip/c720-equities-set`, row 65)

- **A problem set, "A producer beside the price of oil".** A worked example and six questions on what one oil and gas producer filed with the SEC (EOG Resources: revenue, net income, capital spending, debt), set beside the spot price of crude oil on the same days. The last question takes a second producer, of mostly natural gas (Expand Energy), beside the price of gas.
- **It is a waiting set.** It has its page (`/learn/problems/a-producer-beside-the-price-of-oil`) and is in no index, no instructors' note and no dated edition until you approve it. The page is in review like every page.
- **Every figure is real and keyed.** 98 figures, each read from the equities page files by its key: the company's filed periods and the public energy prices. Each is recomputed from the file by the test, and found a second time by the period its question names.
- **No share price is read.** The chain asked for "a segment beside an energy price". A segment's line is built from share prices, and every share price is held ("license needed"), so no segment has a line. The set uses what is public: filed figures. Its test refuses a key into a share price, an index or a segment.
- **It takes no side.** It states what was filed and what a fuel cost, and says in its own words that a price on one day does not explain a quarter's revenue. Its test refuses a word that ranks or advises.

## What the questions find, in the files of 27 November

- EOG's revenue for the quarter to 30 September 2026 was 8,549 USD million, 99.18 percent of the quarter before; the price of WTI on the two last days was 97.18 and 70.56 USD/bbl, 137.73 percent.
- Net income 2,781 USD million, 32.53 percent of revenue. Capital spending over nine months 4,605 USD million, 19.12 percent of nine months' revenue. Debt 7,894 USD million, 227 USD million above a year before.
- Expand Energy's revenue 3,286 USD million, 111.01 percent of the quarter before; Henry Hub 3.02 and 3.34 USD/MMBtu, 90.42 percent.

## Checks

- **The set's Node test:** 589 checks. The first waiting set's test still passes (478 checks).
- **The producer is the rule's:** the test ranks the segment's companies from the list and finds EOG first.
- **Lint:** clean. **Type check** of the problem sets: no error in them (one error of the configuration I wrote for the check, in a file of the Network view it pulled in).
- **The 241 test files that walk the site or name the problem sets or the value check:** 3,079 passed, 97 skipped, 7 failed. Six are the ones that fail on main's own tree on this laptop. The seventh, the listed sets' replication (`test_session7534`), fails the same way on main's tree with my changes set aside. None names this set.
- **Built and seen** at the head (exit 0, 107 s, 2,609 MB free before): the set's page at 1280 and 390 px, every answer open, no page wider than the screen; the index and a listed set do not name it; the value check on both waiting sets' pages, 45 of 45 distinct keys.

## Decisions made without you

- **A company beside a price, not a segment beside a price.** The reason is above.
- **Which producer.** By size, not by how an answer comes out: of the companies of "Exploration and production" whose file holds every period the set reads, the one with the largest revenue for the quarter to 30 September 2026. That is EOG.
- **The second producer is my choice, not a rule:** Expand Energy, one of the five largest of the segment by that quarter's revenue, and a producer of mostly natural gas. That it is "mostly natural gas" is my description and is in no ERW file.
- **A price is read on the last day of a filed period.** A quarter's average price would be the closer comparison; the set says so in its own words and keeps the one-day price, which a student can find in one row.
- **One typed number avoided:** the dates in an answer are written from the set's own period ends, and the words "the debt rose" from the two figures.

## For Samuel's ruling

- **Whether the set is approved** (it then joins the index and the next dated edition), as the forecast's set of session 10404 also waits.
- **Whether the description "a producer of mostly natural gas" may stand** without a source in the warehouse.

## Needs the key

- Nothing. No model was called.

## Next

- Session 10413: the new views at a phone's width by a finger, each through its page's cases; the gaps found on `/equities` mended. Then `/forecast` read on production after rows 63 and 64 land.
